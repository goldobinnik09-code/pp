import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import get_user_menu
from aiogram.types import InlineKeyboardButton
from states import CallsignState
from database import User, Admin, create_tables

logger = logging.getLogger(__name__)
user_router = Router()

# Создание таблиц при инициализации
create_tables()


@user_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    """Обработчик /start"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Участник"
    
    # Проверяем админ ли пользователь
    is_admin = Admin.select().where(Admin.user_id == user_id).exists()
    
    try:
        user = User.get(User.user_id == user_id)
        welcome_text = (
            f"👋 <b>Добро пожаловать обратно, {user_name}!</b>\n\n"
            f"📋 <b>Ваш позывной:</b> <code>{user.callsign}</code>\n\n"
            f"Выберите действие ниже или используйте меню:"
        )
        
        # Если это админ, показываем кнопку админ-панели
        if is_admin:
            welcome_text += "\n\n🔧 <b>Вы администратор!</b>"
            # Берём обычное пользовательское меню и добавляем строку с кнопкой открытия админ-панели
            kb = get_user_menu()
            try:
                kb.inline_keyboard.append([
                    InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_open")
                ])
            except Exception:
                # В редком случае, если get_user_menu вернул не InlineKeyboardMarkup, создаём новый
                from aiogram.types import InlineKeyboardMarkup
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_open")]
                ])

            await message.reply(
                welcome_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
        else:
            await message.reply(
                welcome_text,
                reply_markup=get_user_menu(),
                parse_mode="HTML"
            )
    except User.DoesNotExist:
        greeting_text = (
            f"🎉 <b>Привет, {user_name}!</b>\n\n"
            f"Добро пожаловать в бот управления событиями! 🚀\n\n"
            f"📝 Чтобы начать, введите свой <b>позывной</b> (красивое имя или никнейм):\n"
            f"<i>Например: Ghost, Alpha-1, Viper и т.д.</i>\n\n"
            f"⬇️ Отправьте сообщение с вашим позывным:"
        )
        await message.reply(
            greeting_text,
            parse_mode="HTML"
        )
        await state.set_state(CallsignState.waiting)


@user_router.message(CallsignState.waiting)
async def set_callsign(message: types.Message, state: FSMContext):
    """Установка позывного пользователя"""
    callsign = message.text.strip()
    
    if not callsign:
        await message.reply("❌ Позывной не может быть пустым. Попробуйте ещё раз:")
        return

    if len(callsign) > 50:
        await message.reply("⚠️ Позывной слишком длинный (макс 50 символов). Попробуйте ещё раз:")
        return

    user_id = message.from_user.id
    User.get_or_create(
        user_id=user_id,
        defaults={
            'callsign': callsign,
            'telegram_username': message.from_user.username
        }
    )
    
    await state.clear()
    
    success_text = (
        f"✅ <b>Спасибо!</b> Ваш позывной успешно установлен.\n\n"
        f"🎖️ <b>Позывной:</b> <code>{callsign}</code>\n\n"
        f"📋 <b>Теперь вы можете:</b>\n"
        f"• Просматривать расписание событий\n"
        f"• Отвечать на приглашения\n"
        f"• Быть в списках участников\n\n"
        f"👇 Используйте меню ниже для навигации:"
    )
    
    await message.reply(
        success_text,
        reply_markup=get_user_menu(),
        parse_mode="HTML"
    )

    logger.info(f"Пользователь {user_id} установил позывной: {callsign}")
