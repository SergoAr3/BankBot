from aiogram import Router

import app.db.requests as rq

import app.constans.messages as msg

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove

import app.keyboards.inline_keyboards as kb

base_router = Router()


@base_router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.username
    user_id = message.from_user.id
    menu_button_kb = await kb.get_menu_button_kb()

    await rq.add_user(username, user_id)
    await message.answer(msg.WELCOME_MESSAGE, reply_markup=menu_button_kb)


@base_router.message(Command('menu'))
async def menu(message: Message):
    menu_kb = await kb.get_menu_kb()
    await message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)


@base_router.callback_query(lambda query: query.data == 'menu')
async def menu_callback(callback_query: CallbackQuery):
    menu_kb = await kb.get_menu_kb()
    main_menu_message = await callback_query.message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
    await callback_query.message.delete_reply_markup(str(main_menu_message.message_id))


@base_router.callback_query(lambda query: query.data == 'balance')
async def balance_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_balance = await rq.get_user_balance(user_id)
    await callback_query.message.answer(msg.BALANCE_MESSAGE.format(user_balance))


@base_router.callback_query(
    lambda query: query.data in {'cancel_credit_repay', 'cancel_credit', 'cancel_deposit', 'cancel_deposit_withdraw',
                                 'cancel_transfer'})
async def cancel_deal(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel_transfer':
        menu_kb = await kb.get_menu_kb()
        await callback_query.message.edit_text(msg.TRANSFER_CANCEL_MESSAGE, reply_markup=menu_kb)


    elif callback_query.data == 'cancel_deposit' or callback_query.data == 'cancel_deposit_withdraw':
        deal_kb = await kb.get_deposit_kb()
        message = msg.DEPOSIT_TERMS_MESSAGE
        await callback_query.message.delete()
        await callback_query.message.answer(msg.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        await callback_query.message.answer(message, reply_markup=deal_kb)
        await state.clear()
    else:
        deal_kb = await kb.get_credit_kb()
        message = msg.CREDIT_TERMS_MESSAGE

        await callback_query.message.delete()
        await callback_query.message.answer(msg.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        await callback_query.message.answer(message, reply_markup=deal_kb)
        await state.clear()


@base_router.callback_query(lambda query: query.data == 'cancel')
async def cancel_callback(callback_query: CallbackQuery, state: FSMContext):
    menu_kb = await kb.get_menu_kb()
    await callback_query.message.edit_text(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
    await state.clear()
