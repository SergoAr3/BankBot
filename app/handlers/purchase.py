from aiogram import Router

import app.db.requests as rq
import app.constans.messages as msg
import app.constans.prices as prise

from app.db.model_types import TransactionType

from aiogram.types import CallbackQuery

import app.keyboards.inline_keyboards as kb
from app.handlers import NotEnoughBalanceError

purchase_router = Router()


@purchase_router.callback_query(lambda query: query.data == 'buy_cat')
async def buy_cat_callback(callback_query: CallbackQuery):
    buy_cat_kb = await kb.get_buy_cat_kb()
    await callback_query.message.edit_text(msg.BUY_CAT_MESSAGE, reply_markup=buy_cat_kb)


@purchase_router.callback_query(lambda query: query.data == 'confirm_buy_cat')
async def confirm_buy_cat_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_balance = await rq.get_user_balance(user_id)
    menu_button_kb = await kb.get_menu_button_kb()

    try:
        if user_balance < prise.CAT_IMAGE:
            raise NotEnoughBalanceError
    except NotEnoughBalanceError:
        await callback_query.message.answer(msg.NOT_ENOUGH_BALANCE_ERROR_MESSAGE.format(user_balance), reply_markup=menu_button_kb)
        return

    image = await rq.get_image(user_id)
    if image:
        await rq.change_user_balance(user_id, -prise.CAT_IMAGE)
        await rq.add_transaction(user_id, prise.CAT_IMAGE, TransactionType.PURCHASE)
        await rq.add_cat_buying_info(user_id, image.id)
        await callback_query.message.answer_photo(photo=image.url, caption=msg.BUY_CAT_SUCCESS_MESSAGE,
                                                  reply_markup=menu_button_kb
                                                  )
        await callback_query.answer(msg.WRITE_OFF_CALLBACK_MESSAGE.format(prise.CAT_IMAGE))
        await callback_query.message.bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )
    else:
        await callback_query.message.edit_text(msg.NO_AVAILABLE_CAT_MESSAGE, reply_markup=menu_button_kb)
