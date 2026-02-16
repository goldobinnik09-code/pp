"""
Обработчики для администраторов
"""
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import get_admin_menu, get_events_keyboard
from keyboards.admin_keyboards import get_back_button
from states import AdminCreateEvent, AdminMailing, AdminClearDB
from database import Admin, Event, User

logger = logging.getLogger(__name__)
admin_router = Router()


async def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return Admin.select().where(Admin.user_id == user_id).exists()


@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    """Открытие админ-панели с цветными инлайн кнопками"""
    if await is_admin(message.from_user.id):
        admin_name = message.from_user.first_name or "Администратор"
        panel_text = (
            f"🔧 <b>АДМИН-ПАНЕЛЬ</b>\n\n"
            f"👤 <b>Пользователь:</b> {admin_name}\n"
            f"🎖️ <b>Статус:</b> Администратор\n\n"
        )
        await message.reply(
            panel_text,
            reply_markup=get_admin_menu(),
            parse_mode="HTML"
        )
    else:
        error_text = (
            "❌ <b>ДОСТУП ЗАПРЕЩЁН</b>\n\n"
            "У вас нет прав администратора.\n\n"
            "Если вы считаете что это ошибка, обратитесь к разработчику."
        )
        await message.reply(error_text, parse_mode="HTML")


# ======== Обработчик кнопок админ-панели ========
@admin_router.callback_query(lambda c: c.data.startswith("admin_"))
async def handle_admin_button(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопок админ-панели"""
    # Проверка прав администратора
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора!", show_alert=True)
        return
    
    action = callback.data.replace("admin_", "")
    
    if action == "open":
        # Открыть админ-панель (с кнопки на /start)
        admin_name = callback.from_user.first_name or "Администратор"
        panel_text = (
            f"🔧 <b>АДМИН-ПАНЕЛЬ</b>\n\n"
            f"👤 <b>Пользователь:</b> {admin_name}\n"
            f"🎖️ <b>Статус:</b> Администратор\n\n"
            f"═══════════════════════════"
        )
        await callback.message.edit_text(
            panel_text,
            reply_markup=get_admin_menu(),
            parse_mode="HTML"
        )
        await callback.answer()

    if action == "back":
        # Возврат в админ-панель
        await state.clear()
        admin_name = callback.from_user.first_name or "Администратор"
        panel_text = (
            f"🔧 <b>АДМИН-ПАНЕЛЬ</b>\n\n"
            f"👤 <b>Пользователь:</b> {admin_name}\n"
            f"🎖️ <b>Статус:</b> Администратор\n\n"
            f"═══════════════════════════"
        )
        await callback.message.edit_text(
            panel_text,
            reply_markup=get_admin_menu(),
            parse_mode="HTML"
        )
    elif action == "view_schedule":
            events = Event.select().order_by(Event.date.asc())  # сортировка по дате (ДД.ММ как строка)
            
            if not events.exists():
                await callback.message.edit_text(
                    "📅 <b>Расписание событий</b>\n\n"
                    "ℹ️ Пока нет ни одного события.",
                    reply_markup=get_back_button(),
                    parse_mode="HTML"
                )
                return
            
            schedule_text = "📅 <b>РАСПИСАНИЕ ВСЕХ СОБЫТИЙ</b>\n\n"

            for idx, event in enumerate(events, 1):
                desc = event.description or "— без описания —"

                schedule_text += (
                    f"<b>Событие #{idx}</b>\n"
                    f"Название: {event.name}\n"
                    f"Дата: {event.date}\n"
                    f"Описание: {desc}\n"
                    f"───────────────\n\n"
    )
            
            schedule_text += f"Всего событий: <b>{events.count()}</b>"
            
            await callback.message.edit_text(
                schedule_text,
                reply_markup=get_back_button(),
                parse_mode="HTML"
            )
    elif action == "create_event":
        await callback.message.edit_text(
            "📝 <b>Создание события</b>\n\n"
            "Введите название события:",
            parse_mode="HTML"
        )
        await state.set_state(AdminCreateEvent.name)
    
    elif action == "post_schedule":
        await callback.message.edit_text("⏳ <b>Публикуем расписание...</b>", parse_mode="HTML")
        from handlers.callback_handlers import send_schedule_to_all
        await send_schedule_to_all()
        await callback.message.edit_text(
            "✅ <b>Расписание опубликовано!</b>\n"
            "Все участники получили расписание и опросы по событиям.",
            parse_mode="HTML"
        )
    
    elif action == "post_single_event":
        events = Event.select()
        if not events:
            await callback.message.edit_text("ℹ️ <b>Нет событий</b>\n\nПока нет созданных событий.", parse_mode="HTML")
            return
        await callback.message.edit_text(
            "📋 <b>Выберите событие для публикации:</b>",
            reply_markup=get_events_keyboard(),
            parse_mode="HTML"
        )
    
    elif action == "mailing":
        await callback.message.edit_text(
            "📧 <b>Рассылка сообщения</b>\n\n"
            "Введите текст сообщения (поддерживается HTML разметка):",
            parse_mode="HTML"
        )
        await state.set_state(AdminMailing.message)
    
    elif action == "update_sheet":
        await callback.message.edit_text(
            "⏳ <b>Обновляю таблицу...</b>\n\n"
            "Идёт сбор данных из всех событий...",
            parse_mode="HTML"
        )
        
        # Обновляем все события в таблицу
        try:
            from services.google_sheets import collect_and_update_sheet
         
            
            events = Event.select()
            for event in events:
                await collect_and_update_sheet(event.id)
            
            await callback.message.edit_text(
                "✅ <b>Таблица обновлена!</b>\n\n"
                f"Обновлено событий: {len(list(events))}\n\n"
                "Все ответы участников загружены в Google Sheets",
                parse_mode="HTML"
            )
            logger.info(f"Админ {callback.from_user.id} обновил таблицу вручную")
        except Exception as e:
            await callback.message.edit_text(
                f"❌ <b>Ошибка обновления таблицы:</b>\n\n"
                f"<code>{str(e)}</code>\n\n"
                "Проверьте:<br/>"
                "• credentials.json находится в проекте<br/>"
                "• GOOGLE_SHEET_ID в .env правильный<br/>"
                "• Доступ предоставлен сервисному аккаунту",
                parse_mode="HTML"
            )
            logger.error(f"Ошибка при ручном обновлении таблицы: {e}")
    
    elif action == "clear_database":
        await callback.message.edit_text(
            "⚠️ <b>ВНИМАНИЕ! ОПАСНАЯ ОПЕРАЦИЯ</b>\n\n"
            "❌ <b>ВЫ СОБИРАЕТЕСЬ ОЧИСТИТЬ БАЗУ ДАННЫХ!</b>\n\n"
            "Будут удалены:\n"
            "🗑️ Все события\n"
            "🗑️ Все голоса и ответы участников\n\n"
            "Введите слово <code>ОЧИСТИТЬ</code> чтобы подтвердить:",
            parse_mode="HTML"
        )
        await state.set_state(AdminClearDB.confirm)
    
    await callback.answer()


# ======== Создание события ========
@admin_router.message(AdminCreateEvent.name)
async def admin_event_name(message: types.Message, state: FSMContext):
    """Получение названия события"""
    name = message.text.strip()
    if not name:
        await message.reply("❌ Название не может быть пустым. Попробуйте ещё раз:", reply_markup=get_back_button())
        return
    
    await state.update_data(name=name)
    await state.set_state(AdminCreateEvent.date)
    await message.reply("📅 Введите дату события (формат: ДД.ММ):", reply_markup=get_back_button())


@admin_router.message(AdminCreateEvent.date)
async def admin_event_date(message: types.Message, state: FSMContext):
    """Получение даты события"""
    date = message.text.strip()
    if not date:
        await message.reply("❌ Дата не может быть пустой. Попробуйте ещё раз:", reply_markup=get_back_button())
        return
    
    await state.update_data(date=date)
    await state.set_state(AdminCreateEvent.description)
    await message.reply("📄 Введите описание события (или напишите «нет» для пропуска):", reply_markup=get_back_button())


@admin_router.message(AdminCreateEvent.description)
async def admin_event_desc(message: types.Message, state: FSMContext):
    """Получение описания события и сохранение"""
    desc = None if message.text.lower() in ('нет', 'не нужно', 'без описания') else message.text.strip()
    
    data = await state.get_data()
    Event.create(
        name=data['name'],
        date=data['date'],
        description=desc
    )
    
    await state.clear()
    
    success_text = (
        f"✅ <b>Событие создано успешно!</b>\n\n"
        f"📋 <b>Название:</b> {data['name']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"📝 <b>Описание:</b> {desc or '—'}"
    )
    
    await message.reply(success_text, parse_mode="HTML")
    logger.info(f"Админ {message.from_user.id} создал событие: {data['name']}")


# ======== Рассылка ========
@admin_router.message(AdminMailing.message)
async def send_mailing(message: types.Message, state: FSMContext):
    """Отправка рассылки"""
    from bot_instance import bot
    
    text = message.text
    await state.clear()
    
    users = User.select()
    success = 0
    failed = 0

    # Отправляем сообщение отправителю что идёт рассылка
    status_msg = await message.reply("📧 <b>Рассылаем сообщение...</b>", parse_mode="HTML")

    for user in users:
        try:
            await bot.send_message(user.user_id, text, parse_mode="HTML")
            success += 1
        except Exception as e:
            logger.error(f"Не удалось отправить {user.user_id}: {e}")
            failed += 1

    result_text = (
        f"📊 <b>Рассылка завершена!</b>\n\n"
        f"✅ <b>Успешно:</b> {success}\n"
        f"❌ <b>Ошибок:</b> {failed}\n\n"
        f"📈 <b>Всего пользователей:</b> {success + failed}"
    )
    
    await status_msg.edit_text(result_text, parse_mode="HTML", reply_markup=get_back_button())
    logger.info(f"Рассылка: успешно {success}, ошибок {failed}")


# ======== Очистка базы данных ========
@admin_router.message(AdminClearDB.confirm)
async def confirm_clear_database(message: types.Message, state: FSMContext):
    """Подтверждение и очистка базы данных"""
    text = message.text.strip().upper()
    
    if text != "ОЧИСТИТЬ":
        await message.reply(
            "❌ Неверный код подтверждения!\n\n"
            "Введите <code>ОЧИСТИТЬ</code> чтобы подтвердить:",
            parse_mode="HTML",
            reply_markup=get_back_button()
        )
        return
    
    await state.clear()
    
    # Удаляем все события и ответы
    from database import UserEventResponse
    
    events_count = Event.select().count()
    responses_count = UserEventResponse.select().count()
    
    status_msg = await message.reply(
        "🗑️ <b>Очищаю базу данных...</b>",
        parse_mode="HTML"
    )
    
    try:
        # Удаляем все ответы и события
        UserEventResponse.delete().execute()
        Event.delete().execute()
        
        await status_msg.edit_text(
            f"✅ <b>БАЗА ДАННЫХ УСПЕШНО ОЧИЩЕНА!</b>\n\n"
            f"🗑️ Удалено событий: {events_count}\n"
            f"🗑️ Удалено голосов: {responses_count}\n\n"
            f"📋 Информация о пользователях сохранена",
            parse_mode="HTML",
            reply_markup=get_back_button()
        )
        logger.warning(f"⚠️ DBCLEAN: Админ {message.from_user.id} удалил {events_count} событий и {responses_count} голосов")
    
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>ОШИБКА при очистке!</b>\n\n"
            f"<code>{str(e)}</code>",
            parse_mode="HTML",
            reply_markup=get_back_button()
        )
        logger.error(f"Ошибка при очистке БД: {e}")
