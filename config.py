from os import getenv

import pytz
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from loguru import logger

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher

load_dotenv()


class BotConfig:
    DISPATCHER = Dispatcher()
    TOKEN = getenv('BOT_TOKEN')

    @staticmethod
    def get_bot():
        if not BotConfig.TOKEN:
            logger.error("Токен бота не найден!")
            raise ValueError("Токен бота не задан в переменных среды!")
        bot = Bot(token=BotConfig.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        return bot


class DataBaseConfig:
    HOST = getenv('DB_HOST')
    PORT = getenv('DB_PORT')
    USER = getenv('POSTGRES_USER')
    PASSWORD = getenv('POSTGRES_PASSWORD')
    NAME = getenv('POSTGRES_DB')

    @staticmethod
    def get_connection():
        if not all([DataBaseConfig.USER, DataBaseConfig.PASSWORD, DataBaseConfig.NAME]):
            logger.error("Учетные данные базы данных неполны!")
            raise ValueError("Учетные данные базы данных неполные в переменных среды!")
        connection = f'postgresql+asyncpg://{DataBaseConfig.USER}:{DataBaseConfig.PASSWORD}@{DataBaseConfig.HOST}:{DataBaseConfig.PORT}/{DataBaseConfig.NAME}'
        return connection

    @staticmethod
    def get_engine():
        try:
            connection = DataBaseConfig.get_connection()
            engine = create_async_engine(connection)
            return engine
        except Exception as e:
            logger.error(f"Не удалось создать базы данных: {e}")


class RedisConfig:
    HOST = getenv('REDIS_HOST')
    PORT = getenv('REDIS_PORT')

    @staticmethod
    def get_connection():
        if not all([RedisConfig.HOST, RedisConfig.PORT]):
            logger.error("Учетные данные Redis неполны!")
            raise ValueError("Учетные данные Redis неполные в переменных среды!")
        connection = f'redis://{RedisConfig.HOST}:{RedisConfig.PORT}/0'
        return connection

class AsyncIOSchedulerConfig:

    @staticmethod
    def get_trigger(due_date):
        trigger = DateTrigger(run_date=due_date, timezone=pytz.timezone('Europe/Moscow'))
        return trigger


bot = BotConfig.get_bot()
