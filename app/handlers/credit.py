from aiogram import Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app.db.requests as rq
import app.constans.messages as msg
import app.constans.deadlines as dl
from app.handlers.exceptions import NegativeAmountError, NotEnoughBalanceError, ExceedsCreditLimitError, \
    ExceedsDebtAmountError
from app.utils.states import Credit
from app.db.model_types import CreditJobType, ScheduledJobType
import app.utils.schedule_tasks as task

from loguru import logger
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from datetime import datetime, timedelta

import app.keyboards.inline_keyboards as kb
import app.keyboards.replay_keyboards as rkb
from config import AsyncIOSchedulerConfig

credit_router = Router()


@credit_router.callback_query(lambda query: query.data == 'back_credit_menu')
@credit_router.callback_query(lambda query: query.data == 'credit')
async def credit_callback(callback_query: CallbackQuery):
    credit_kb = await kb.get_credit_kb()
    await callback_query.message.edit_text(msg.CREDIT_TERMS_MESSAGE, reply_markup=credit_kb)


@credit_router.callback_query(lambda query: query.data == 'take_credit')
async def take_credit_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_credits = await rq.get_active_user_credits(user_id)
    if len(user_credits) > dl.CREDIT_COUNT_LIMIT:
        back_credit_menu_button_kb = await kb.get_back_credit_menu_button_kb()
        await callback_query.message.answer(msg.CREDITS_LIMIT_MESSAGE, reply_markup=back_credit_menu_button_kb)
    else:
        choice_deadline_kb = await rkb.get_choice_deadline_kb()
        await callback_query.message.bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )
        await callback_query.message.answer(msg.CHOICE_DEADLINE_MESSAGE, reply_markup=choice_deadline_kb)

    await state.set_state(Credit.deadline)
    await state.update_data(user_credits=user_credits)


@credit_router.message(Credit.deadline)
async def get_credit_deadline(message: Message, state: FSMContext):
    if message.text == dl.DEADLINE_1_MESSAGE:
        choice_credit_amount_kb_1 = await rkb.get_choice_amount_kb_1()
        await message.answer(msg.INPUT_CREDIT_AMOUNT_MESSAGE_1, reply_markup=choice_credit_amount_kb_1)
        await state.update_data(credit_deadline=dl.DEADLINE_1)
        await state.set_state(Credit.amount_1)


    elif message.text == dl.DEADLINE_2_MESSAGE:
        user_id = message.from_user.id
        user_credit = await rq.check_user_credit(user_id)
        if user_credit >= dl.CREDIT_COUNT_LIMIT_2:
            await message.answer(msg.CREDIT2_LIMIT_MESSAGE)

        choice_credit_amount_kb_2 = await rkb.get_choice_amount_kb_2()
        await message.answer(msg.INPUT_CREDIT_AMOUNT_MESSAGE_2, reply_markup=choice_credit_amount_kb_2)
        await state.set_state(Credit.amount_2)

    elif message.text == msg.CANCEL_BUTTON_MESSAGE:
        menu_kb = await kb.get_menu_kb()
        await message.answer(msg.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        await message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
        await state.clear()

    else:
        choice_deadline_kb = await rkb.get_choice_deadline_kb()
        await message.answer(msg.DEADLINE_ERROR_MESSAGE, reply_markup=choice_deadline_kb)


@credit_router.callback_query(lambda query: query.data == 'confirm_credit')
async def credit_confirm(callback_query: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    state_data = await state.get_data()
    credit_percent = state_data.get('credit_percent')
    due_date = state_data.get('due_date')
    credit_amount = state_data.get('credit_amount')
    user_id = callback_query.from_user.id
    credit_info = await rq.add_credit(user_id, credit_amount, due_date, credit_percent)
    credit_id = credit_info.get('credit_info')
    remaining_debt = credit_info.get('remaining_debt')

    trigger = AsyncIOSchedulerConfig.get_trigger(due_date)

    job = apscheduler.add_job(task.debt_reminder_and_accrual, trigger=trigger,
                              args=[user_id, credit_id, due_date, credit_amount, credit_percent,
                                    remaining_debt, apscheduler])
    logger.info(f'Пользователь {callback_query.from_user.username}_{user_id} взял кредит на сумму {credit_amount}. '
                f'Запустилась задача на проверку просрочки и увеличению долга: {job.trigger}, next_run_time={job.next_run_time}')

    await rq.add_scheduled_job(job.id, credit_id, due_date, deal_type=ScheduledJobType.CREDIT,

                               job_type=CreditJobType.DEBT_REMINDER)

    menu_button_kb = await kb.get_menu_button_kb()
    await callback_query.message.answer(
        msg.CREDIT_SUCCESS_MESSAGE.format(credit_amount, dl.DEADLINE_2_MESSAGE,
                                          due_date.strftime('%d.%m.%Y'), dl.CREDIT_PERCENT_2),
        reply_markup=ReplyKeyboardRemove())
    await callback_query.message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_button_kb)
    await state.clear()


@credit_router.callback_query(lambda query: query.data in {'back_active_user_credits', 'credits_info'})
async def credits_info_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_credits = await rq.get_active_user_credits(user_id)
    if user_credits:
        user_active_credits_kb = await kb.get_user_active_credits_kb(user_credits)

        await callback_query.message.edit_text(msg.USER_ACTIVE_CREDITS_MESSAGE, reply_markup=user_active_credits_kb)
    else:
        back_credit_menu_button_kb = await kb.get_back_credit_menu_button_kb()
        await callback_query.message.edit_text(msg.USER_NOT_ACTIVE_CREDITS_MESSAGE,
                                               reply_markup=back_credit_menu_button_kb)


@credit_router.callback_query(lambda query: 'active_credit_' in query.data)
async def active_credit_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Credit.info)
    credit_id = int(callback_query.data[14:])
    credit_info = await rq.get_credit(credit_id)

    user_credit_info_kb = await kb.get_user_credit_info_kb(credit_id)
    credit_term = credit_info.term.strftime('%d.%m.%Y')
    await callback_query.message.edit_text(
        msg.CREDIT_INFO_MESSAGE.format(credit_info.amount, credit_info.percent, credit_term,
                                       credit_info.remaining_debt),
        reply_markup=user_credit_info_kb)

    await state.update_data(credit_info=credit_info, credit_id=credit_id)


@credit_router.callback_query(lambda query: 'repay_credit_' in query.data)
async def credit_repay_callback(callback_query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    credit_id = state_data.get('credit_id')
    credit_info = state_data.get('credit_info')
    credit_term = credit_info.term
    credit_percent = credit_info.percent
    remaining_debt = int(credit_info.remaining_debt)
    cancel_button = await kb.get_cancel_button()
    repay_credit_message = await callback_query.message.answer(msg.CREDIT_REPAY_MESSAGE.format(remaining_debt),
                                                               reply_markup=cancel_button)
    await callback_query.message.delete_reply_markup(str(repay_credit_message.message_id - 1))

    await state.update_data(credit_id=credit_id, remaining_debt=remaining_debt, credit_term=credit_term,
                            credit_percent=credit_percent)
    await state.set_state(Credit.repay)


@credit_router.message(Credit.repay)
async def credit_repay(message: Message, state: FSMContext):
    cancel_button = await kb.get_cancel_button()
    state_data = await state.get_data()
    remaining_debt = state_data.get('remaining_debt')
    user_id = message.from_user.id
    user_balance = await rq.get_user_balance(user_id)


    await message.bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id - 1,
        reply_markup=None
    )
    try:
        repay_amount = float(message.text)
        if repay_amount <= 0:
            raise NegativeAmountError

        elif repay_amount > user_balance:
            raise NotEnoughBalanceError

        elif repay_amount > remaining_debt:
            raise ExceedsDebtAmountError
    except (ValueError, NegativeAmountError):
        await message.answer(msg.NEGATIVE_AMOUNT_ERROR_MESSAGE.format(remaining_debt), reply_markup=cancel_button)
        return
    except NotEnoughBalanceError:
        await message.answer(msg.NOT_ENOUGH_BALANCE_ERROR_MESSAGE.format(user_balance), reply_markup=cancel_button)
        return
    except ExceedsDebtAmountError:
        await message.answer(msg.EXCEEDS_DEBT_AMOUNT_ERROR.format(remaining_debt), reply_markup=cancel_button)
        return

    await state.update_data(repay_amount=repay_amount)
    confirm_kb = await kb.get_confirm_kb('credit_repay')

    await message.answer(
        msg.CREDIT_REPAY_CONFIRM_MESSAGE.format(repay_amount),
        reply_markup=confirm_kb
    )

    await state.set_state(Credit.repay_confirm)


@credit_router.callback_query(lambda query: query.data == 'confirm_credit_repay')
async def credit_repay_confirm(callback_query: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):
    state_data = await state.get_data()
    credit_id = state_data.get('credit_id')
    repay_amount = state_data.get('repay_amount')
    credit_term = state_data.get('credit_term')
    credit_percent = state_data.get('credit_percent')
    remaining_debt = state_data.get('remaining_debt')
    menu_button_kb = await kb.get_menu_button_kb()
    new_remaining_debt = remaining_debt - repay_amount


    if new_remaining_debt == 0:
        job_id = await rq.delete_job(deal_id=credit_id, deal_type=ScheduledJobType.CREDIT)
        if apscheduler.get_job(job_id):
            apscheduler.remove_job(job_id)

        await rq.repay_credit(credit_id, repay_amount, closed=True)
        await callback_query.message.edit_text(msg.CREDIT_FULL_REPAY_SUCCESS_MESSAGE,
                                               reply_markup=menu_button_kb)
    else:
        await rq.repay_credit(credit_id, repay_amount)

        if credit_percent == dl.CREDIT_PERCENT_1:
            elapsed_credit_days = (credit_term - datetime.now()).days
            if elapsed_credit_days > 0:
                await callback_query.message.edit_text(
                    msg.CREDIT_PARTIAL_REPAY_SUCCESS_MESSAGE.format(repay_amount, new_remaining_debt,
                                                                    elapsed_credit_days),
                    reply_markup=menu_button_kb)
            else:
                days_overdue = 7 + elapsed_credit_days
                await callback_query.message.edit_text(
                    msg.CREDIT_PARTIAL_REPAY_AFTER_TERM_SUCCESS_MESSAGE.format(repay_amount, new_remaining_debt, days_overdue),
                    reply_markup=menu_button_kb)

        else:
            elapsed_credit_days = (credit_term - datetime.now()).days + 1

            if elapsed_credit_days > 0:
                await callback_query.message.edit_text(
                    msg.CREDIT_PARTIAL_REPAY_SUCCESS_MESSAGE.format(repay_amount, new_remaining_debt,
                                                                    elapsed_credit_days),
                    reply_markup=menu_button_kb)
            else:
                days_overdue = 7 + elapsed_credit_days
                await callback_query.message.edit_text(
                    msg.CREDIT_PARTIAL_REPAY_AFTER_TERM_SUCCESS_MESSAGE.format(repay_amount, new_remaining_debt,
                                                                    days_overdue),
                    reply_markup=menu_button_kb)


@credit_router.callback_query(lambda query: query.data == 'back')
async def back_callback(callback_query: CallbackQuery, state: FSMContext):
    menu_kb = await kb.get_menu_kb()
    await callback_query.message.edit_text(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)

    await state.clear()


@credit_router.message()
async def get_credit_amount(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in {Credit.amount_1, Credit.amount_2}:

        if message.text == msg.CANCEL_BUTTON_MESSAGE:
            menu_kb = await kb.get_menu_kb()
            await message.answer(msg.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
            await message.answer(msg.MAIN_MENU_MESSAGE, reply_markup=menu_kb)
            await state.clear()
            return

        credit_percent = dl.CREDIT_PERCENT_1
        credit_deadline = dl.DEADLINE_1
        credit_limit = dl.CREDIT_LIMIT_1

        if current_state == Credit.amount_2:
            credit_percent = dl.CREDIT_PERCENT_2
            credit_deadline = dl.DEADLINE_2
            credit_limit = dl.CREDIT_LIMIT_2

        cancel_button = await kb.get_cancel_button()
        try:

            amount = float(message.text)
            if amount <= 0:
                raise NegativeAmountError

            elif amount > credit_limit:
                raise ExceedsCreditLimitError

        except (ValueError, NegativeAmountError):
            await message.answer(msg.NEGATIVE_AMOUNT_ERROR_MESSAGE.format(credit_limit), reply_markup=cancel_button)
            return
        except ExceedsCreditLimitError:
            await message.answer(msg.EXCEEDS_CREDIT_LIMIT_ERROR_MESSAGE.format(credit_limit), reply_markup=cancel_button)
            return

        amount = float(message.text)
        confirm_kb = await kb.get_confirm_kb('credit')
        due_date = datetime.now() + timedelta(days=credit_deadline)
        await state.update_data(credit_amount=amount, credit_percent=credit_percent, due_date=due_date)

        await message.answer(
            msg.CREDIT_CONFIRM_MESSAGE.format(amount, due_date.strftime('%d.%m.%Y'), credit_percent),
            reply_markup=confirm_kb
        )



    await state.set_state(Credit.confirm)
