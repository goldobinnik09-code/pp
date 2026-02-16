"""
Клавиатуры для администраторов с цветными инлайн кнопками
"""
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from database import Event


def get_admin_menu() -> InlineKeyboardMarkup:
    """Получить меню администратора с цветными инлайн кнопками
    
    🟢 success - зелёная для создания нового события
    🔵 primary - синяя для основных действий (публикация)
    🔴 danger - красная для осторожных действий
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Создать ивент",
                callback_data="admin_create_event",
                style="success"  # 🟢 Зелёная - позитивное действие
            ),
        ],
        [
            InlineKeyboardButton(
                text="📢 Опубликовать расписание",
                callback_data="admin_post_schedule",
                style="primary"  # 🔵 Синяя - основная функция
            ),
        ],
        [
                InlineKeyboardButton(text="📅 Расписание событий", callback_data="admin_view_schedule", style="primary"),
            
        ],
        [
            InlineKeyboardButton(
                text="📋 Один ивент",
                callback_data="admin_post_single_event",
                style="primary"  # 🔵 Синяя - основная функция
            ),
            InlineKeyboardButton(
                text="📧 Рассылка",
                callback_data="admin_mailing",
                style="primary"  # 🔵 Синяя - основная функция
            ),
        
        ],
        [
            InlineKeyboardButton(
                text="📊 Обновить таблицу",
                callback_data="admin_update_sheet",
                style="primary"  # 🔵 Синяя - просмотр данных
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Очистить базу",
                callback_data="admin_clear_database",
                style="danger"  # 🔴 Красная - опасное действие
            ),
        ],
    ])
    return keyboard


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка 'Назад' для возврата в админ-панель"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Назад в админ-панель",
                callback_data="admin_back",
                style="primary"
            ),
        ],
    ])


def get_back_button_with_submit(submit_text: str = "Отправить") -> InlineKeyboardMarkup:
    """Кнопка Назад + дополнительная кнопка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Отмена",
                callback_data="admin_back",
                style="primary"
            ),
        ],
    ])


def get_events_keyboard() -> InlineKeyboardMarkup:
    """Получить клавиатуру с событиями для публикации
    
    🔵 primary - синяя кнопка для основной функции (публикация события)
    📅 - иконка календаря для визуального отличие
    """
    events = Event.select()
    
    if not events:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for event in events:
        button = [InlineKeyboardButton(
            text=f"📅 {event.date} — {event.name}",
            callback_data=f"post_event_{event.id}",
            style="primary"  # 🔵 Синяя кнопка для основного действия
        )]
        keyboard.inline_keyboard.append(button)
    
    return keyboard
