"""
Обработчики callback-кнопок
"""
import logging
import datetime
import asyncio
import pytz
from aiogram import Router, types
from keyboards.user_keyboards import get_event_response_keyboard
from database import User, Event, UserEventResponse
from services import schedule_collection, collect_and_update_sheet
from config import SCHEDULE_COLLECTION_DAYS, DEFAULT_TIMEZONE

logger = logging.getLogger(__name__)
callback_router = Router()


def get_moscow_tz():
    """Получить временную зону Москвы"""
    return pytz.timezone(DEFAULT_TIMEZONE)


async def send_schedule_to_all():
    """Отправка расписания всем пользователям"""
    from bot_instance import bot
    
    events = Event.select()
    if not events:
        return

    schedule_text = "📋 <b>Расписание на неделю:</b>\n\n"
    for e in events:
        schedule_text += f"📅 <b>{e.date}</b>: {e.name}\n"

    users = User.select()

    for user in users:
        try:
            await bot.send_message(user.user_id, schedule_text, parse_mode="HTML")
            for event in events:
                await send_event_poll(user.user_id, event, bot)
        except Exception as e:
            logger.error(f"Ошибка отправки расписания {user.user_id}: {e}")


async def send_event_to_all(event: Event):
    """Отправка одного события всем пользователям"""
    from bot_instance import bot
    
    users = User.select()
    for user in users:
        try:
            await send_event_poll(user.user_id, event, bot)
        except Exception as e:
            logger.error(f"Ошибка отправки события {user.user_id}: {e}")


async def send_event_poll(user_id: int, event: Event, bot):
    """Отправка опроса по событию"""
    keyboard = get_event_response_keyboard(event.id)

    text = (
        f"<b>🎯 Событие:</b> {event.name}\n"
        f"<b>📅 Дата:</b> {event.date}\n"
        f"<b>📝 Описание:</b> {event.description or '—'}\n\n"
        f"<b>Сможете прийти?</b>"
    )

    msg = await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="HTML")

    # Планирование сбора результатов через N дней
    collect_time = datetime.datetime.now(get_moscow_tz()) + datetime.timedelta(days=SCHEDULE_COLLECTION_DAYS)
    asyncio.create_task(schedule_collection(event.id, collect_time))


@callback_router.callback_query(lambda c: c.data.startswith('post_event_'))
async def handle_post_event(callback: types.CallbackQuery):
    """Обработка публикации события"""
    event_id = int(callback.data.split('_')[-1])
    event = Event.get_by_id(event_id)
    
    await send_event_to_all(event)
    await callback.message.edit_text(
        f"✅ Событие <b>«{event.name}»</b> отправлено всем участникам.",
        parse_mode="HTML"
    )
    await callback.answer()

    logger.info(f"Событие {event.name} опубликовано")


@callback_router.callback_query(lambda c: c.data.startswith('response_'))
async def handle_response(callback: types.CallbackQuery):
    """Обработка ответа участника на событие (ТОЛЬКО ОДИН РАЗ!)"""
    parts = callback.data.split('_')
    will_come = parts[1] == 'yes'
    event_id = int(parts[2])
    user_id = callback.from_user.id

    try:
        user = User.get(User.user_id == user_id)
        event = Event.get_by_id(event_id)
        
        # Проверка что пользователь уже ответил
        existing_response = UserEventResponse.select().where(
            (UserEventResponse.user == user) & (UserEventResponse.event == event)
        ).first()
        
        if existing_response:
            # ❌ БЛОКИРУЕМ ИЗМЕНЕНИЕ ГОЛОСА
            current_status = "✅ согласились" if existing_response.response else "❌ отказались"
            await callback.answer(
                f"⛔ Вы уже голосовали!\n\n"
                f"Ваш ответ: {current_status}\n"
                f"Изменить ответ нельзя",
                show_alert=True
            )
            logger.info(f"🚫 BLOCKED: @{user.telegram_username or 'unknown'}({user.callsign}) пытался изменить ответ для '{event.name}'")
        else:
            # ✅ НОВЫЙ ОТВЕТ - ЗАПИСЫВАЕМ И СРАЗУ СИНХРОНИЗИРУЕМ
            UserEventResponse.create(
                user=user,
                event=event,
                response=will_come
            )
            status_text = "✅ Буду!" if will_come else "❌ Не буду"
            
            # Обновляем исходное сообщение с событием
            from keyboards.user_keyboards import get_response_submitted_keyboard
            
            response_status = "✅ согласились" if will_come else "❌ отказались"
            new_text = (
                f"<b>🎯 Событие:</b> {event.name}\n"
                f"<b>📅 Дата:</b> {event.date}\n"
                f"<b>📝 Описание:</b> {event.description or '—'}\n\n"
                f"<b>✓ Спасибо за ответ!</b>\n\n"
                f"🎖️ <b>Ваш ответ:</b> {response_status}\n"
                f"📍 <b>Время голосования:</b> <code>{datetime.datetime.now().strftime('%H:%M:%S')}</code>\n\n"
                f"<i>Ваш голос записан и отправлен в таблицу</i>"
            )
            
            await callback.message.edit_text(
                new_text,
                reply_markup=get_response_submitted_keyboard(will_come),
                parse_mode="HTML"
            )
            
            await callback.answer(f"✓ Голос учтён: {status_text}", show_alert=False)
            logger.info(f"✍️  RECORDED: @{user.telegram_username or 'unknown'}({user.callsign}) = {status_text} для '{event.name}'")
            
            # 🔄 СРАЗУ СИНХРОНИЗИРУЕМ В GOOGLE SHEETS
            try:
                from services.google_sheets import collect_and_update_sheet
                asyncio.create_task(collect_and_update_sheet(event_id))
                logger.info(f"📊 SYNC: Таблица обновлена для события '{event.name}'")
            except Exception as e:
                logger.error(f"⚠️  Не удалось обновить таблицу сразу: {e}")
        
        # Обновляем username если изменился
        if user.telegram_username != callback.from_user.username:
            user.telegram_username = callback.from_user.username
            user.save()

    except User.DoesNotExist:
        await callback.answer("❌ Ошибка в БД", show_alert=True)
        logger.error(f"❌ User {user_id} not found in DB")


@callback_router.callback_query(lambda c: c.data == 'already_voted')
async def handle_already_voted(callback: types.CallbackQuery):
    """Обработка нажатия на кнопку 'Вы уже проголосовали'"""
    await callback.answer("ℹ️ Ваш голос уже записан!", show_alert=False)
