"""
Работа с Google Sheets
"""
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE
from database import Event, UserEventResponse, User

logger = logging.getLogger(__name__)


async def collect_and_update_sheet(event_id: int):
    """Запись результатов ответов в Google Таблицу в красивом формате
    
    Формат таблицы:
    Ник телеграмма | Позывной | Дата события | Ответ
    @username      | Иван     | 2026-02-11   | ✅ Буду
    @username      | Иван     | 2026-02-12   | ❌ Не буду
    """
    try:
        event = Event.get_by_id(event_id)
        
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_CREDENTIALS_FILE,
            scope
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

        # Получаем все данные
        all_events = Event.select()
        all_responses = UserEventResponse.select()
        all_users = User.select()
        
        # Заголовок таблицы
        headers = ["👤 Ник в Telegram", "🎖️ Позывной", "📅 Дата события", "✍️ Ответ"]
        
        # Очищаем лист и добавляем заголовок
        sheet.clear()
        sheet.append_row(headers)
        
        rows_to_add = []
        
        # Собираем все записи
        for event in all_events:
            for user in all_users:
                # Ищем ответ пользователя на это событие
                response = UserEventResponse.select().where(
                    (UserEventResponse.user == user) & 
                    (UserEventResponse.event == event)
                ).first()
                
                username = f"@{user.telegram_username}" if user.telegram_username else "—"
                event_date = event.date
                answer = "✅ Буду" if response and response.response else ("❌ Не буду" if response else "— Нет ответа")
                
                rows_to_add.append([username, user.callsign, event_date, answer])
        
        # Добавляем все строки в таблицу
        if rows_to_add:
            sheet.append_rows(rows_to_add)
            logger.info(f"📊 Таблица обновлена: добавлено {len(rows_to_add)} записей")
        else:
            logger.info("📊 Таблица обновлена: нет ответов для записи")

    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении таблицы: {e}")
