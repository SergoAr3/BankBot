from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

import app.db.requests as rq
import app.constans.messages as msg

from typing import Dict, Any, Callable, Awaitable
from loguru import logger


class CheckUserBlockingMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]):
        user_id = event.callback_query.from_user.id if event.callback_query else event.message.from_user.id
        is_blocked = await rq.check_user_blocking(user_id)

        if is_blocked:
            await event.bot.send_message(chat_id=user_id, text=msg.USER_BLOCKING_MESSAGE)
            return
        return await handler(event, data)
#
