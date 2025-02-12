import app.db.requests as rq
import app.constans.messages as msg

from app.db.model_types import ScheduledJobType, CreditJobType

from config import bot, AsyncIOSchedulerConfig
from datetime import datetime, timedelta
from loguru import logger


async def send_first_warning_message(user_id, credit_amount, credit_percent) -> None:
    await bot.send_message(chat_id=user_id,
                           text=msg.CREDIT_FIRST_WARNING_MESSAGE.format(credit_amount, credit_percent))


async def send_warning_message(user_id, credit_amount, new_remaining_debt, days_overdue) -> None:
    await bot.send_message(chat_id=user_id,
                           text=msg.CREDIT_WARNING_MESSAGE.format(credit_amount, new_remaining_debt, days_overdue))


async def send_last_warning_message(user_id) -> None:
    await bot.send_message(chat_id=user_id, text=msg.CREDIT_LAST_WARNING_MESSAGE)


async def block_user(user_id, credit_id):
    await rq.block_user(user_id)
    await rq.delete_job(credit_id, ScheduledJobType.CREDIT)


async def debt_reminder_and_accrual(user_id, credit_id, due_date, credit_amount, credit_percent,
                                    remaining_debt,
                                    apscheduler):
    job_id = await rq.delete_job(deal_id=credit_id, deal_type=ScheduledJobType.CREDIT)
    if apscheduler.get_job(job_id):
        apscheduler.remove_job(job_id)

    days_overdue = (datetime.now() - due_date).days

    if days_overdue == 0:
        logger.info(f"Беспроцентный период для пользователя {user_id} закончился!")
        await send_first_warning_message(user_id, credit_amount, credit_percent)
        await rq.delete_job(credit_id, ScheduledJobType.CREDIT)

        due_date = datetime.now() + timedelta(days=1)
        trigger = AsyncIOSchedulerConfig.get_trigger(due_date)

        job = apscheduler.add_job(debt_reminder_and_accrual, trigger=trigger,
                                  args=[user_id, user_id, credit_id, due_date, credit_amount, credit_percent,
                                        remaining_debt, apscheduler])

        await rq.add_scheduled_job(job.id, credit_id, due_date, deal_type=ScheduledJobType.CREDIT,
                                   job_type=CreditJobType.DEBT_REMINDER)

    if 0 < days_overdue < 7:
        new_remaining_debt = remaining_debt * (1 + (credit_percent / 100))
        await rq.credit_debt_accrual(credit_id, new_remaining_debt)
        logger.info(f"Пользователь {user_id} просрочил платеж на  {days_overdue} дней.")
        await send_warning_message(user_id, credit_amount, new_remaining_debt, days_overdue)
        await rq.delete_job(credit_id, ScheduledJobType.CREDIT)

        due_date = datetime.now() + timedelta(days=1)
        trigger = AsyncIOSchedulerConfig.get_trigger(due_date)

        job = apscheduler.add_job(debt_reminder_and_accrual, trigger=trigger,
                                  args=[user_id, user_id, credit_id, due_date, credit_amount, credit_percent,
                                        new_remaining_debt,
                                        apscheduler])
        logger.info('Новая задача запустилась')

        await rq.add_scheduled_job(job.id, credit_id, due_date, deal_type=ScheduledJobType.CREDIT,
                                   job_type=CreditJobType.DEBT_REMINDER)

    elif days_overdue == 7:
        new_remaining_debt = remaining_debt * (1 + (credit_percent / 100))
        await rq.repay_credit(credit_id, new_remaining_debt)
        logger.info(f"Последнее предупреждение для пользователя {user_id}.")
        await send_last_warning_message(user_id)
        await rq.delete_job(credit_id, ScheduledJobType.CREDIT)

        due_date = datetime.now() + timedelta(days=1)
        trigger = AsyncIOSchedulerConfig.get_trigger(due_date)
        job = apscheduler.add_job(block_user, trigger=trigger, args=[user_id, credit_id])
        await rq.add_scheduled_job(job.id, credit_id, due_date, deal_type=ScheduledJobType.CREDIT,
                                   job_type=CreditJobType.BLOCK_USER)


async def deposit_payment(user_id, deposit_id, deposit_amount, apscheduler):
    job_id = await rq.delete_job(deal_id=deposit_id, deal_type=ScheduledJobType.DEPOSIT)
    await rq.withdraw_deposit(deposit_id, user_id, deposit_amount)

    if apscheduler.get_job(job_id):
        apscheduler.remove_job(job_id)
