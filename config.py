"""
Конфигурация приложения
"""
import os

# Telegram Bot
BOT_TOKEN = '8586648065:AAH6-24B71j00BIUMLRy6wWLtWVYXmFXn1Y'


# Google Sheets
GOOGLE_SHEET_ID = '1GdKpyGwzbzKk5VuMCRa0DToqw4PuYLe41ZWrSegWcwU'
GOOGLE_CREDENTIALS_FILE = 'cred.json'

# Database
DATABASE_PATH = 'bot.db'

# Logging
LOG_LEVEL = 'INFO'

# Timezone
DEFAULT_TIMEZONE = 'Europe/Moscow'

# Scheduling
SCHEDULE_COLLECTION_DAYS = 3
AUTO_POST_SCHEDULE_DAY = 6  # 6 = Sunday
AUTO_POST_SCHEDULE_TIME = "20:00"
