"""
Телеграм-бот для управления событиями и расписанием
Использует aiogram 3, peewee и Google Sheets
"""

import logging
import asyncio
import sys
from pathlib import Path

from aiogram import Dispatcher
from aiogram.types import BotCommand

from bot_instance import bot
from handlers import user_router, admin_router, callback_router
from services.scheduler import setup_scheduler, scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Диспетчер
dp = Dispatcher()

# Подключение роутеров
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(callback_router)


async def set_default_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Начать работу"),
        BotCommand(command="admin", description="🔧 Администратор"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")


async def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("🤖 ЗАПУСК ТЕЛЕГРАМ-БОТА ДЛЯ УПРАВЛЕНИЯ СОБЫТИЯМИ")
    logger.info("=" * 60)
    
    try:
        # Получение информации о боте
        me = await bot.get_me()
        logger.info(f"✅ Бот инициализирован: @{me.username} (ID: {me.id})")
        logger.info(f"📝 Имя: {me.first_name}")
        
        # Установка команд
        logger.info("📋 Установка команд бота...")
        await set_default_commands()
        logger.info("✅ Команды установлены")
        
        # Инициализация планировщика
        logger.info("⏰ Инициализация планировщика...")
        setup_scheduler()
        asyncio.create_task(scheduler())
        logger.info("✅ Планировщик запущен")
        
        logger.info("=" * 60)
        logger.info("🎯 БОТ ГОТОВ К РАБОТЕ!")
        logger.info("=" * 60)
        logger.info("📲 Ожидание сообщений...")
        logger.info("💡 Команды: /start, /admin")
        logger.info("⌨️  Нажмите Ctrl+C для остановки")
        logger.info("=" * 60)
        
        # Начало polling
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("⛔ БОТ ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        logger.info("🛑 Закрытие соединения...")
        await bot.session.close()
        logger.info("✅ Бот выключен")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение закрыто")
        sys.exit(0)