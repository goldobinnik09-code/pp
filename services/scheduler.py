"""
Работа с расписанием и автоматизацией
"""
import asyncio
import logging
import datetime
import pytz
import schedule
from config import DEFAULT_TIMEZONE, AUTO_POST_SCHEDULE_DAY, AUTO_POST_SCHEDULE_TIME, SCHEDULE_COLLECTION_DAYS

logger = logging.getLogger(__name__)


def get_moscow_tz():
    """Получить временную зону Москвы"""
    return pytz.timezone(DEFAULT_TIMEZONE)


async def schedule_collection(event_id: int, collect_time: datetime.datetime):
    """Планирование сбора результатов через N дней"""
    delay = (collect_time - datetime.datetime.now(get_moscow_tz())).total_seconds()
    if delay > 0:
        logger.info(f"Сбор результатов события {event_id} запланирован через {delay} сек")
        await asyncio.sleep(delay)
    
    # Отложенный импорт для избежания циклической зависимости
    from services.google_sheets import collect_and_update_sheet
    await collect_and_update_sheet(event_id)


async def scheduler():
    """Основной цикл планировщика"""
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)


def setup_scheduler():
    """Инициализация расписания"""
    logger.info("Планировщик инициализирован")
