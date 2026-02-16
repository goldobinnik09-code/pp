"""
Инициализация бота
Отдельный модуль для хранения экземпляра Bot
"""

from aiogram import Bot
from config import BOT_TOKEN

# Инициализировать бота один раз
bot = Bot(token=BOT_TOKEN)
