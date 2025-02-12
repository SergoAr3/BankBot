import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DataBaseConfig

import app.db.models as model

from sqlalchemy import select, delete, update
from app.db.model_types import ScheduledJobType, CreditJobType, TransactionType

engine = DataBaseConfig.get_engine()
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_user(user_id: int = None, username: str = None):
    async with async_session() as session:
        if user_id:
            user = await session.execute(
                select(model.User).where(model.User.id == user_id)
            )

            user = user.scalar_one_or_none()
            return user
        else:
            user = await session.execute(
                select(model.User).where(model.User.username == username)
            )
            user = user.scalar_one_or_none()

            return user


async def get_user_balance(user_id: int):
    async with async_session() as session:
        balance = await session.scalar(select(model.User.balance).where(model.User.id == user_id))

        return balance


async def add_user(username: str, user_id: int = None) -> None:
    async with async_session() as session:
        check_user = await session.scalar(
            select(model.User.id).where(model.User.id == user_id))
        if not check_user:
            session.add(model.User(id=user_id, username=username))
            await session.commit()


async def add_transaction(user_id: int, amount: int, job_type: TransactionType, description: int = None):
    async with async_session() as session:
        session.add(model.Transaction(user_id=user_id, amount=amount, type=job_type, description=description))
        await session.commit()


async def change_user_balance(user_id: int, amount: int):
    async with async_session() as session:
        await session.execute(
            update(model.User).where(model.User.id == user_id).values(
                balance=model.User.balance + amount))

        await session.commit()


async def add_channel_subscription_info(user_id: int, channel_id: int):
    async with async_session() as session:
        session.add(model.ChannelSubscription(channel_id=channel_id, user_id=user_id))
        await session.commit()


async def add_scheduled_job(job_id: str, deal_id: int, run_time: datetime.datetime,
                            deal_type: ScheduledJobType,
                            job_type: CreditJobType = None):
    async with async_session() as session:
        if deal_type == ScheduledJobType.CREDIT:
            session.add(
                model.ScheduledCreditJob(apscheduler_job_id=job_id, credit_id=deal_id, type=job_type,
                                         run_time=run_time))
            await session.commit()

        elif deal_type == ScheduledJobType.DEPOSIT:
            session.add(model.ScheduledDepositJob(apscheduler_job_id=job_id, deposit_id=deal_id,
                                                  run_time=run_time))
            await session.commit()


async def delete_job(deal_id: int, deal_type: ScheduledJobType):
    async with async_session() as session:
        if deal_type == ScheduledJobType.CREDIT:
            job_id = await session.execute(
                delete(model.ScheduledCreditJob)
                .where(model.ScheduledCreditJob.credit_id == deal_id)
                .returning(model.ScheduledCreditJob.apscheduler_job_id)
            )
            await session.commit()

        elif deal_type == ScheduledJobType.DEPOSIT:
            job_id = await session.execute(
                delete(model.ScheduledDepositJob)
                .where(model.ScheduledDepositJob.deposit_id == deal_id)
                .returning(model.ScheduledDepositJob.apscheduler_job_id)
            )

            await session.commit()

        job_id = job_id.scalar_one_or_none()
        return job_id


async def block_user(user_id: int):
    async with async_session() as session:
        user = await session.execute(
            select(model.User).where(model.User.id == user_id)
        )

        user = user.scalar_one_or_none()

        user.blocking = True

        await session.commit()


async def check_user_blocking(user_id: int):
    async with async_session() as session:
        blocking = await session.execute(
            select(model.User.blocking).where(model.User.id == user_id)
        )

        blocking = blocking.scalar_one_or_none()

        return blocking

# async def restore_jobs():
#     async with async_session() as session:
#         try:
#             result = await session.execute(select(ScheduledJob))
#         except DBAPIError as e:
#             logger.error(e)
#         if result:
#             for job_row in result:
#                 job = job_row.ScheduledJob
#                 func = f'app.utils.task_scheduler:{job.func_name}'
#                 chat_id = job.chat_id
#                 hour = job.hour
#                 minute = job.minute
#                 seconds = job.seconds
#                 state = FSMContext(storage=storage,
#                                    key=StorageKey(bot_id=bot.id, chat_id=chat_id, user_id=chat_id))
#                 args = [bot, chat_id, chat_id, state, scheduler]
#                 if job.type == 'main':
#                     trigger = CronTrigger(day_of_week='mon-fri', hour=hour, minute=minute,
#                                           timezone=pytz.timezone('Europe/Moscow'))
#                     block_job = scheduler.add_job(func, trigger, args=args, id=job.job_id)
#                     old_job = await rq.get_job_id(chat_id, 1)
#                     await rq.delete_job(old_job)
#                     job_interval = datetime.strptime(f'{hour}:{minute}', '%H:%M').time()
#                     await rq.set_block_job(chat_id, block_job.id, 1, job_interval)
#
#                 elif job.type == 'skip_or_restart':
#                     trigger = CronTrigger(day_of_week='mon-fri', start_date=job.start_date, hour=hour, minute=minute,
#                                           timezone=pytz.timezone('Europe/Moscow'))
#                     block_job = scheduler.add_job(func, trigger, args=args, id=job.job_id)
#                     old_job = await rq.get_job_id(chat_id, 1)
#                     await rq.delete_job(old_job)
#                     job_interval = datetime.strptime(f'{hour}:{minute}', '%H:%M').time()
#                     await rq.set_block_job(chat_id, block_job.id, 1, job_interval)
#
#                 else:
#                     trigger = 'interval'
#                     waiting_job = scheduler.add_job(func, trigger, seconds=seconds, args=args, id=job.job_id)
#                     old_job = await rq.get_job_id(chat_id, 2)
#                     await rq.delete_job(old_job)
#                     await rq.set_waiting_job(chat_id, waiting_job.id, 2)
#                 logger.info(f'Восстановилась задача {job.job_id}')
