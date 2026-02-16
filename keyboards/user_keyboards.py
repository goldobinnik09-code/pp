"""
Клавиатуры для обычных пользователей с цветными кнопками
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


def get_user_menu() -> InlineKeyboardMarkup:
    """Получить меню для обычного пользователя"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Соцсети",
                url="https://example.com/social",
                 style="primary" 
            ),
        ],
        [
            InlineKeyboardButton(
                text="📊 Таблицы",
                url="https://docs.google.com/spreadsheets/d/ВАШ_ID"
            ),
        ],
    ])
    return keyboard


def get_event_response_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для ответа на событие с цветными кнопками
    
    🟢 success - зелёная кнопка для согласия
    🔴 danger - красная кнопка для отказа
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Буду",
                callback_data=f"response_yes_{event_id}",
                style="success"  # 🟢 Зелёная кнопка
            ),
            InlineKeyboardButton(
                text="❌ Не буду",
                callback_data=f"response_no_{event_id}",
                style="danger"   # 🔴 Красная кнопка
            ),
        ],
    ])
    return keyboard


def get_response_submitted_keyboard(response: bool) -> InlineKeyboardMarkup:
    """Клавиатура после голосования - информационная кнопка
    
    Показывает что пользователь уже проголосовал
    """
    status_text = "✅ Вы согласились - буду!" if response else "❌ Вы отказались - не буду"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=status_text,
                callback_data="already_voted",
            ),
        ],
    ])
    return keyboard
