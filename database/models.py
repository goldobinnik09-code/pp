"""
Модели базы данных
"""
import datetime
import peewee as pw
from config import DATABASE_PATH

db = pw.SqliteDatabase(DATABASE_PATH)


class BaseModel(pw.Model):
    """Базовая модель для всех таблиц"""
    class Meta:
        database = db


class User(BaseModel):
    """Модель пользователя"""
    user_id = pw.BigIntegerField(unique=True, primary_key=True)
    callsign = pw.CharField(max_length=255)
    telegram_username = pw.CharField(max_length=255, null=True)  # @username в Telegram
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'users'


class Admin(BaseModel):
    """Модель администратора"""
    user_id = pw.BigIntegerField(unique=True, primary_key=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'admins'


class Event(BaseModel):
    """Модель события"""
    id = pw.AutoField(primary_key=True)
    name = pw.CharField(max_length=255)
    date = pw.CharField(max_length=50)
    description = pw.TextField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'events'


class UserEventResponse(BaseModel):
    """Модель ответа пользователя на событие"""
    id = pw.AutoField(primary_key=True)
    user = pw.ForeignKeyField(User, backref='responses', on_delete='CASCADE')
    event = pw.ForeignKeyField(Event, backref='responses', on_delete='CASCADE')
    response = pw.BooleanField()
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'user_event_responses'
        indexes = ((('user', 'event'), True),)


def create_tables():
    """Создание всех таблиц в БД"""
    db.create_tables([User, Admin, Event, UserEventResponse])
