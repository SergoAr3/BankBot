import asyncio

from loguru import logger
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.handlers.base import router
from app.keyboards.default_commands import set_commands

load_dotenv()


async def main():
    logger.info("Starting bot")
    dp = Dispatcher()
    bot = Bot(token=getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
