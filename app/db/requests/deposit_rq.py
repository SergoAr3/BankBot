import datetime

import app.db.models as model

from sqlalchemy import select, update, insert

from app.db.requests.base_rq import async_session


async def get_deposit(deposit_id: int):
    async with async_session() as session:
        deposit = await session.execute(
            select(model.Deposit).where(model.Deposit.id == deposit_id)
        )

        deposit = deposit.scalar_one_or_none()

        return deposit


async def add_deposit(user_id: int, amount: float, percent: int, payment_date: datetime.datetime, payment_amount: float):
    async with async_session() as session:
        added_deposit_id = await session.execute(
            insert(model.Deposit).values(user_id=user_id, amount=amount, payment_date=payment_date, percent=percent,
                                         payment_amount=payment_amount).returning(model.Deposit.id))
        added_deposit_id = added_deposit_id.scalar_one_or_none()

        await session.execute(
            update(model.User).where(model.User.id == user_id).values(balance=model.User.balance - amount))

        await session.commit()
        return added_deposit_id


async def get_active_user_deposits(user_id: int):
    async with async_session() as session:
        user_deposits = await session.execute(
            select(model.Deposit)
            .select_from(model.Deposit)
            .join(model.User, model.Deposit.user_id == model.User.id)
            .where(model.User.id == user_id, model.Deposit.completed == False)
        )

        user_deposits = user_deposits.scalars().all()

        return user_deposits


async def withdraw_deposit(deposit_id: int, user_id: int, deposit_amount: float):
    async with async_session() as session:
        await session.execute(
            update(model.Deposit).where(model.Deposit.id == deposit_id).values(
                completed=True))

        await session.execute(
            update(model.User).where(model.User.id == user_id).values(
                balance=model.User.balance + deposit_amount))

        await session.commit()
