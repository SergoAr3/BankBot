from aiogram import Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app.db.requests as rq
import app.constans.messages as msg
import app.constans.deadlines as dl
from app.handlers import NegativeAmountError, NotEnoughBalanceError
from app.utils.states import Deposit
from app.db.model_types import ScheduledJobType
import app.utils.schedule_tasks as task

from loguru import logger
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from datetime import datetime, timedelta

import app.keyboards.inline_keyboards as kb
import app.keyboards.replay_keyboards as rkb
from config import AsyncIOSchedulerConfig

deposit_router = Router()


@deposit_router.callback_query(lambda query: query.data == 'back_deposit_menu')
@deposit_router.callback_query(lambda query: query.data == 'deposit')
async def deposit_callback(callback_query: CallbackQuery):
    deposit_kb = await kb.get_deposit_kb()
    await callback_query.message.edit_text(msg.DEPOSIT_TERMS_MESSAGE, reply_markup=deposit_kb)


@deposit_router.callback_query(lambda query: query.data == 'take_deposit')
async def take_deposit_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_deposits = await rq.get_active_user_deposits(user_id)

    if len(user_deposits) >= dl.DEPOSIT_COUNT_LIMIT:
        deposit_credit_menu_button_kb = await kb.get_deposit_credit_menu_button_kb()
        await callback_query.message.edit_text(msg.DEPOSIT_LIMIT_MESSAGE, reply_markup=deposit_credit_menu_button_kb)
        return

    choice_deadline_kb = await rkb.get_choice_deadline_kb()
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )
    await callback_query.message.answer(msg.CHOICE_DEADLINE_MESSAGE, reply_markup=choice_deadline_kb)

    await state.set_state(Deposit.deadline)


@deposit_router.message(Deposit.deadline)
async def get_deposit_deadline(message: Message, state: FSMContext):
    if message.text == dl.DEADLINE_1_MESSAGE or message.text == dl.DEADLINE_2_MESSAGE:
        choice_deposit_amount_kb = await rkb.get_choice_amount_kb_2()
        await message.answer(msg.INPUT_DEPOSIT_AMOUNT_MESSAGE, reply_markup=choice_deposit_amount_kb)
        if message.text == dl.DEADLINE_1_MESSAGE:
            await state.update_data(deposit_deadline=dl.DEADLINE_1, deposit_percent=dl.DEPOSIT_PERCENT_1)
        else:
            await state.update_data(deposit_deadline=dl.DEADLINE_2, deposit_percent=dl.DEPOSIT_PERCENT_2)
        await state.set_state(Deposit.amount)
    elif message.text == msg.CANCEL_BUTTON_MESSAGE:
        menu_kb = await kb.get_menu_kb()
        await message.answer(msg.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        await message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
        await state.clear()
    else:
        choice_deadline_kb = await rkb.get_choice_deadline_kb()
        await message.answer(msg.DEADLINE_ERROR_MESSAGE, reply_markup=choice_deadline_kb)


@deposit_router.message(Deposit.amount)
async def get_deposit_amount(message: Message, state: FSMContext):
    if message.text == msg.CANCEL_BUTTON_MESSAGE:
        menu_kb = await kb.get_menu_kb()
        await message.answer(msg.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        await message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
        await state.clear()
        return

    user_id = message.from_user.id
    user_balance = await rq.get_user_balance(user_id)
    cancel_button = await kb.get_cancel_button()

    try:
        deposit_amount = float(message.text)
        logger.info(deposit_amount)
        if deposit_amount <= 0:
            raise NegativeAmountError

        elif deposit_amount > user_balance:
            raise NotEnoughBalanceError
    except (ValueError, NegativeAmountError):
        await message.answer(msg.NEGATIVE_AMOUNT_ERROR_MESSAGE.format(user_balance), reply_markup=cancel_button)
        return
    except (ValueError, NotEnoughBalanceError):
        await message.answer(msg.NOT_ENOUGH_BALANCE_ERROR_MESSAGE.format(user_balance), reply_markup=cancel_button)
        return

    confirm_kb = await kb.get_confirm_kb('deposit')
    state_data = await state.get_data()
    deposit_deadline = state_data.get('deposit_deadline')
    deposit_percent = state_data.get('deposit_percent')
    payment_date = datetime.now() + timedelta(days=deposit_deadline)
    payment_amount = round(deposit_amount * ((1 + (deposit_percent / 100)) ** deposit_deadline), 2)

    await state.update_data(deposit_amount=deposit_amount, deposit_percent=deposit_percent, payment_date=payment_date,
                            payment_amount=payment_amount)

    await message.answer(
        msg.DEPOSIT_CONFIRM_MESSAGE.format(deposit_amount, deposit_deadline, deposit_percent, payment_amount,
                                           round((payment_amount - deposit_amount), 2)),
        reply_markup=confirm_kb
    )
    await state.set_state(Deposit.confirm)


@deposit_router.callback_query(lambda query: query.data == 'confirm_deposit')
async def deposit_confirm(callback_query: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    state_data = await state.get_data()
    deposit_percent = state_data.get('deposit_percent')
    payment_date = state_data.get('payment_date')
    deposit_amount = state_data.get('deposit_amount')
    payment_amount = state_data.get('payment_amount')
    user_id = callback_query.from_user.id
    logger.info(deposit_amount)
    deposit_id = await rq.add_deposit(user_id, deposit_amount, deposit_percent, payment_date, payment_amount)

    trigger = AsyncIOSchedulerConfig.get_trigger(payment_date)

    job = apscheduler.add_job(task.deposit_payment, trigger=trigger,
                              args=[user_id, deposit_id, deposit_amount, apscheduler])
    logger.info(
        f'Пользователь {callback_query.from_user.username}_{user_id} открыл вклад на сумму {deposit_amount}. '
        f'Запустилась задача на выплату {payment_amount} монет: {job.trigger}')

    await rq.add_scheduled_job(job.id, deposit_id, payment_date, deal_type=ScheduledJobType.DEPOSIT)

    menu_kb = await kb.get_menu_kb()
    await callback_query.message.answer(
        msg.DEPOSIT_SUCCESS_MESSAGE.format(deposit_amount, dl.DEADLINE_2_MESSAGE,
                                           payment_date.strftime('%d.%m.%Y'), dl.CREDIT_PERCENT_2),
        reply_markup=ReplyKeyboardRemove())
    await callback_query.answer(msg.WRITE_OFF_CALLBACK_MESSAGE.format(deposit_amount))
    await callback_query.message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
    await state.clear()


@deposit_router.callback_query(lambda query: query.data == 'back_active_user_deposits')
@deposit_router.callback_query(lambda query: query.data == 'deposits_info')
async def deposits_info_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_deposits = await rq.get_active_user_deposits(user_id)
    if user_deposits:
        user_active_deposits_kb = await kb.get_user_active_deposits_kb(user_deposits)

        await callback_query.message.edit_text(msg.USER_ACTIVE_DEPOSITS_MESSAGE, reply_markup=user_active_deposits_kb)
    else:
        back_deposit_menu_button_kb = await kb.get_deposit_credit_menu_button_kb()
        await callback_query.message.edit_text(msg.USER_NOT_ACTIVE_DEPOSITS_MESSAGE,
                                               reply_markup=back_deposit_menu_button_kb)


@deposit_router.callback_query(lambda query: 'active_deposit_' in query.data)
async def active_deposit_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Deposit.info)
    deposit_id = int(callback_query.data[15:])
    deposit_info = await rq.get_deposit(deposit_id)
    deposit_deadline = dl.DEADLINE_2
    deposit_amount = deposit_info.amount
    if deposit_info.percent == 1:
        deposit_deadline = dl.DEADLINE_1

    user_deposit_info_kb = await kb.get_user_deposit_info_kb(deposit_id)
    await callback_query.message.edit_text(
        msg.DEPOSIT_INFO_MESSAGE.format(deposit_amount, deposit_info.percent, deposit_deadline,
                                        deposit_info.payment_amount),
        reply_markup=user_deposit_info_kb)

    await state.update_data(deposit_id=deposit_id, deposit_info=deposit_info, deposit_deadline=deposit_deadline,
                            deposit_amount=deposit_amount)


@deposit_router.callback_query(lambda query: 'withdraw_deposit_' in query.data)
async def withdraw_deposit_callback(callback_query: CallbackQuery):
    deposit_withdraw_kb = await kb.get_deposit_withdraw_kb()
    deposit_withdraw_message = await callback_query.message.answer(msg.DEPOSIT_WITHDRAW_MESSAGE,
                                                                   reply_markup=deposit_withdraw_kb)
    await callback_query.message.delete_reply_markup(str(deposit_withdraw_message.message_id - 1))


@deposit_router.callback_query(lambda query: query.data == 'continue_withdraw')
async def deposit_withdraw(callback_query: CallbackQuery):
    confirm_kb = await kb.get_confirm_kb('deposit_withdraw')
    await callback_query.message.edit_text(
        msg.DEPOSIT_WITHDRAW_CONFIRM_MESSAGE,
        reply_markup=confirm_kb
    )


@deposit_router.callback_query(lambda query: query.data == 'confirm_deposit_withdraw')
async def deposit_withdraw(callback_query: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    state_data = await state.get_data()
    deposit_id = state_data.get('deposit_id')
    deposit_amount = state_data.get('deposit_amount')
    user_id = callback_query.from_user.id

    job_id = await rq.delete_job(deal_id=deposit_id, deal_type=ScheduledJobType.DEPOSIT)
    await rq.withdraw_deposit(deposit_id, user_id, deposit_amount)

    if apscheduler.get_job(job_id):
        apscheduler.remove_job(job_id)

    menu_button_kb = await kb.get_menu_button_kb()
    await callback_query.message.edit_text(
        msg.DEPOSIT_WITHDRAW_SUCCESS_MESSAGE,
        reply_markup=menu_button_kb
    )

    await state.clear()
