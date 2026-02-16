"""
Состояния для FSM
"""
from aiogram.fsm.state import StatesGroup, State


class CallsignState(StatesGroup):
    """Состояния для установки позывного"""
    waiting = State()


class AdminCreateEvent(StatesGroup):
    """Состояния для создания события администратором"""
    name = State()
    date = State()
    description = State()


class AdminMailing(StatesGroup):
    """Состояния для рассылки сообщений"""
    message = State()


class AdminClearDB(StatesGroup):
    """Состояния для очистки базы данных"""
    confirm = State()
