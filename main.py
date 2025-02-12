import asyncio

from loguru import logger

from app.handlers import base_router, channels_router, credit_router, deposit_router, purchase_router, transfer_router
from app.keyboards.default_commands import set_commands
from app.middlewares.blocking_middleware import CheckUserBlockingMiddleware
from app.middlewares.scheduler_middleware import SchedulerMiddleware
from config import BotConfig, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def main():
    logger.info("Starting bot")
    scheduler = AsyncIOScheduler()
    dp = BotConfig.DISPATCHER
    dp.include_routers(base_router, purchase_router, deposit_router,
                       transfer_router, channels_router, credit_router)
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(CheckUserBlockingMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    scheduler.start()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
