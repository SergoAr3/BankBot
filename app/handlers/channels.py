import time

from aiogram import Router
from aiogram.enums import ChatMemberStatus

import app.db.requests as rq
import app.constans.messages as msg
import app.utils.redis_client as redis_client
import app.constans.prices as price

from aiogram.types import CallbackQuery

import app.keyboards.inline_keyboards as kb
from app.constans.cooldown import COOLDOWN_SECONDS, COOLDOWN_MESSAGE

channels_router = Router()


@channels_router.callback_query(lambda query: query.data == 'channels')
async def channels_callback(callback_query: CallbackQuery):
    check_subscriptions_button = await kb.get_check_subscriptions_button()
    user_tg_id = callback_query.from_user.id
    channels = await rq.get_channels(user_tg_id)
    channels_list = '\n'.join(
        [f"{rank}. @{channel.name}" for rank, channel in enumerate(channels, start=1)])

    if channels_list:
        await callback_query.message.answer(msg.CHANNELS.format(channels_list), reply_markup=check_subscriptions_button,
                                            disable_web_page_preview=True)
    else:
        await callback_query.message.answer(msg.CHANNELS_0)


@channels_router.callback_query(lambda query: query.data == 'check_subscriptions')
async def check_subscriptions_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    last_used = await redis_client.get_cooldown(user_id)
    current_time = int(time.time())
    if last_used and current_time - int(last_used) < COOLDOWN_SECONDS:
        await callback_query.answer(COOLDOWN_MESSAGE, show_alert=True)
        return

    await redis_client.set_cooldown(user_id, COOLDOWN_SECONDS, current_time)

    channels = await rq.get_channels(user_id)
    count_subscribed_channels = 0

    for channel in channels:
        member = await callback_query.bot.get_chat_member(chat_id=f'@{channel.name}', user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            count_subscribed_channels += 1
            await rq.add_channel_subscription_info(user_id=user_id, channel_id=channel.id)

    if count_subscribed_channels > 0:
        menu_button_kb = await kb.get_menu_button_kb()
        amount = price.CHANNEL_SUBSCRIBE * count_subscribed_channels
        await callback_query.message.answer(
            msg.CHECK_SUBSCRIPTIONS.format(count_subscribed_channels, amount), reply_markup=menu_button_kb)
        await callback_query.answer(msg.CREDITING_CALLBACK_MESSAGE.format(amount))
        await rq.change_user_balance(user_id, amount)
    else:
        await callback_query.message.answer(msg.CHECK_SUBSCRIPTIONS_0)
