from aiogram import Router

import app.db.requests as rq
import app.constans.messages as msg
from app.handlers import NotEnoughBalanceError, NegativeAmountError

from app.utils.states import Transfer
from app.db.model_types import TransactionType

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards.inline_keyboards as kb

transfer_router = Router()


@transfer_router.callback_query(lambda query: query.data == 'transfer')
async def transfer_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Transfer.amount)
    cancel_button = await kb.get_cancel_button()
    await callback_query.message.answer(msg.TRANSFER_MESSAGE1, reply_markup=cancel_button)


@transfer_router.message(Transfer.amount)
async def transfer_amount(message: Message, state: FSMContext):
    cancel_button = await kb.get_cancel_button()
    user_id = message.from_user.id
    user_balance = await rq.get_user_balance(user_id)

    await message.bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id - 1,
        reply_markup=None
    )
    try:
        amount = float(message.text)

        if amount <= 0:
            raise NegativeAmountError

        elif user_balance < amount:
            raise NotEnoughBalanceError

    except (ValueError, NegativeAmountError):
        await message.answer(msg.NEGATIVE_AMOUNT_ERROR_MESSAGE.format(user_balance), reply_markup=cancel_button)
        return
    except NotEnoughBalanceError:
        await message.answer(msg.NOT_ENOUGH_BALANCE_ERROR_MESSAGE.format(user_balance), reply_markup=cancel_button)
        return

    await state.update_data(amount=message.text)
    await state.set_state(Transfer.username)
    await message.answer(msg.TRANSFER_MESSAGE2, reply_markup=cancel_button)


@transfer_router.message(Transfer.username)
async def transfer_username(message: Message, state: FSMContext):
    cancel_button = await kb.get_cancel_button()
    await message.bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id - 1,
        reply_markup=None
    )

    username = message.text.split()[0]
    if username[0] == '@':
        username = username[1:]

    user = await rq.get_user(username=username)
    if not user:
        await message.answer(msg.TRANSFER_USERNAME_ERROR_MESSAGE.format(username),
                             reply_markup=cancel_button)

        return

    await state.update_data(username=username, recipient_id=user.id)
    data = await state.get_data()
    amount = data.get('amount')
    confirm_kb = await kb.get_confirm_kb('transfer')

    await state.set_state(Transfer.confirm)

    await message.answer(
        msg.TRANSFER_CONFIRM_MESSAGE.format(amount, username),
        reply_markup=confirm_kb
    )


@transfer_router.callback_query(lambda query: query.data == 'confirm_transfer')
async def transfer_confirm(callback_query: CallbackQuery, state: FSMContext):
    transfer_data = await state.get_data()
    amount = float(transfer_data.get("amount"))
    sender_username = callback_query.from_user.username
    recipient_id = transfer_data.get("recipient_id")
    sender_id = callback_query.from_user.id

    await rq.transfer(sender_id, recipient_id, amount)

    sender_balance = await rq.get_user_balance(sender_id)
    recipient_balance = await rq.get_user_balance(recipient_id)
    await rq.add_transaction(sender_id, -100, TransactionType.TRANSFER)
    await rq.add_transaction(recipient_id, 100, TransactionType.TRANSFER)

    await callback_query.message.edit_text(msg.TRANSFER_SUCCESS_MESSAGE.format(sender_balance), reply_markup=None)
    await callback_query.answer(msg.WRITE_OFF_CALLBACK_MESSAGE.format(amount))
    await callback_query.bot.send_message(
        chat_id=recipient_id,
        text=msg.TRANSFER_NOTIFICATION_MESSAGE.format(sender_username, amount, recipient_balance)
    )
    await state.clear()
