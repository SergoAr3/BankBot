from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllGroupChats


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Главное меню"),
        # BotCommand(command="balance", description="Узнать баланс"),
        # BotCommand(command="transfer", description="Перевести монеты"),
        # BotCommand(command="buy_cat", description="Купить котика"),
        # BotCommand(command="credit", description="Взять кредит"),
        # BotCommand(command="credit_info", description="Мой кредит"),
        # BotCommand(command="deposit", description="Открыть вклад"),
        # BotCommand(command="deposit_info", description="Мои вклады"),
        # BotCommand(command="subscriptions", description="Подписки на каналы"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
