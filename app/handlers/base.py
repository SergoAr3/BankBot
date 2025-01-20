from dotenv import load_dotenv

import app.db.requests as rq
import app.constans.messages as msg
import app.constans.prices as prise
from app.utils.states import Transfer
from app.db.models import TransactionType

from aiogram import Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

import app.keyboards.inline_keyboards as kb

load_dotenv()
router = Router()


@router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.username
    user_id = message.from_user.id
    start_kb = await kb.get_start_kb()

    await rq.add_user(username, user_id)
    await message.answer(msg.WELCOME_MESSAGE, reply_markup=start_kb)


@router.message(Command('menu'))
async def menu(message: Message):
    menu_kb = await kb.get_menu_kb()
    main_menu_message = await message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)

@router.callback_query(lambda query: query.data == 'menu')
async def menu_callback(callback_query: CallbackQuery):
    menu_kb = await kb.get_menu_kb()
    main_menu_message = await callback_query.message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
    await callback_query.message.delete_reply_markup(str(main_menu_message.message_id))


@router.callback_query(lambda query: query.data == 'balance')
async def balance_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_balance = await rq.get_user_balance(user_id)
    await callback_query.message.answer(msg.BALANCE_MESSAGE.format(user_balance))


@router.callback_query(lambda query: query.data == 'transfer')
async def transfer_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Transfer.amount)
    cancel_button = await kb.get_cancel_button()
    await callback_query.message.answer(msg.TRANSFER_MESSAGE1, reply_markup=cancel_button)


@router.message(Transfer.amount)
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
        amount = int(message.text)
        if user_balance < amount:
            await message.answer(msg.TRANSFER_BALANCE_ERROR_MESSAGE, reply_markup=cancel_button)

            return

        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(msg.TRANSFER_AMOUNT_ERROR_MESSAGE, reply_markup=cancel_button)

        return

    await state.update_data(amount=message.text)
    await state.set_state(Transfer.username)
    await message.answer(msg.TRANSFER_MESSAGE2, reply_markup=cancel_button)


@router.message(Transfer.username)
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

    user_id = await rq.get_user_tg_id(username=username)
    if not user_id:
        await message.answer(msg.TRANSFER_USERNAME_ERROR_MESSAGE.format(username),
                             reply_markup=cancel_button)

        return

    await state.update_data(username=username, recipient_id=user_id)
    data = await state.get_data()
    amount = data['amount']
    confirm_kb = await kb.get_transfer_confirm_kb()

    await state.set_state(Transfer.confirm)

    await message.answer(
        msg.TRANSFER_CONFIRM_MESSAGE.format(amount, username),
        reply_markup=confirm_kb
    )


@router.callback_query(lambda query: query.data in ['confirm_transfer', 'cancel_transfer'])
async def transfer_confirm(callback_query: CallbackQuery, state: FSMContext):
    menu_kb = await kb.get_menu_kb()
    if callback_query.data == "cancel_transfer":
        await callback_query.message.edit_text(msg.TRANSFER_CANCEL_MESSAGE, reply_markup=menu_kb)
        return

    transfer_data = await state.get_data()
    amount = int(transfer_data.get("amount"))
    sender_username = callback_query.from_user.username
    recipient_tg_id = transfer_data.get("recipient_id")
    sender_tg_id = callback_query.from_user.id
    recipient_id = await rq.get_user_id(recipient_tg_id)
    sender_id = await rq.get_user_id(sender_tg_id)

    await rq.transfer(sender_tg_id, recipient_tg_id, amount)

    sender_balance = await rq.get_user_balance(sender_tg_id)
    recipient_balance = await rq.get_user_balance(recipient_tg_id)
    await rq.add_transaction(sender_id, -100, TransactionType.TRANSFER)
    await rq.add_transaction(recipient_id, 100, TransactionType.TRANSFER)

    await callback_query.message.edit_text(msg.TRANSFER_SUCCESSFUL_MESSAGE.format(sender_balance), reply_markup=None)
    await callback_query.bot.send_message(
        chat_id=recipient_tg_id,
        text=msg.TRANSFER_NOTIFICATION_MESSAGE.format(sender_username, amount, recipient_balance)
    )
    await state.clear()


@router.callback_query(lambda query: query.data == 'buy_cat')
async def buy_cat_callback(callback_query: CallbackQuery):
    buy_cat_kb = await kb.get_buy_cat_kb()
    await callback_query.message.answer(msg.BUY_CAT_MESSAGE, reply_markup=buy_cat_kb)


@router.callback_query(lambda query: query.data == 'confirm_buy_cat')
async def confirm_buy_cat_callback(callback_query: CallbackQuery):
    tg_user_id = callback_query.from_user.id
    user_id = await rq.get_user_id(tg_user_id=tg_user_id)
    user_balance = await rq.get_user_balance(tg_user_id)
    menu_button = await kb.get_menu_button()
    if user_balance < prise.CAT_IMAGE:
        await callback_query.message.answer(msg.BUY_CAT_ERROR_MESSAGE, reply_markup=menu_button)
        return

    image = await rq.get_image(tg_user_id)
    await rq.reduce_user_balance(tg_user_id, prise.CAT_IMAGE)
    await rq.add_transaction(user_id, prise.CAT_IMAGE, TransactionType.PURCHASE)
    await rq.add_cat_buying_info(user_id, image.id)
    await callback_query.message.answer_photo(photo=image.url, caption=msg.BUY_CAT_SUCCESSFUL_MESSAGE, reply_markup=menu_button
                                              )
    await callback_query.message.bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )


@router.callback_query(lambda query: query.data == 'back')
async def back_callback(callback_query: CallbackQuery, state: FSMContext):
    menu_kb = await kb.get_menu_kb()
    chat_id = callback_query.from_user.id
    main_menu_message = await callback_query.message.edit_text(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
    await callback_query.message.bot.delete_message(chat_id=chat_id, message_id=main_menu_message.message_id - 1)

    await state.clear()

@router.callback_query(lambda query: query.data == 'cancel')
async def cancel_callback(callback_query: CallbackQuery, state: FSMContext):
    menu_kb = await kb.get_menu_kb()
    await callback_query.message.edit_text(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
    await state.clear()
