import datetime

import app.db.models as model
import app.constans.deadlines as dl

from sqlalchemy import select, update, insert

from loguru import logger

from app.db.requests.base_rq import async_session



async def get_credit(credit_id: int):
    async with async_session() as session:
        credit = await session.execute(
            select(model.Credit).where(model.Credit.id == credit_id)
        )

        credit = credit.scalar_one_or_none()

        return credit




async def add_credit(user_id: int, amount: float, term: datetime.datetime, percent: int):
    async with async_session() as session:
        added_credit_info = await session.execute(
            insert(model.Credit).values(user_id=user_id, amount=amount, term=term, percent=percent,
                                        remaining_debt=amount).returning(model.Credit.id,
                                                                         model.Credit.remaining_debt))
        added_credit_info = added_credit_info.all()

        added_credit_info = {
            'credit_info': added_credit_info[0][0],
            'remaining_debt': added_credit_info[0][1]
        }

        await session.commit()
        return added_credit_info


async def check_user_credit(user_id: int):
    async with async_session() as session:
        user_credit = await session.execute(
            select(model.Credit)
            .select_from(model.Credit)
            .join(model.User, model.Credit.user_id == model.User.id)
            .where(model.User.id == user_id, model.Credit.percent == dl.CREDIT_PERCENT_2)
        )
        user_credit = user_credit.scalar_one_or_none()
        logger.info(user_credit)

        return user_credit


async def get_active_user_credits(user_id: int):
    async with async_session() as session:
        user_credits = await session.execute(
            select(model.Credit)
            .select_from(model.Credit)
            .join(model.User, model.Credit.user_id == model.User.id)
            .where(model.User.id == user_id, model.Credit.closed == False)
        )

        user_credits = user_credits.scalars().all()

        return user_credits


async def repay_credit(credit_id: int, amount: float, closed: bool = False):
    async with async_session() as session:
        if closed:
            await session.execute(
                update(model.Credit).where(model.Credit.id == credit_id).values(
                    remaining_debt=model.Credit.remaining_debt - amount,
                    closed=closed))
            await session.commit()
        else:
            await session.execute(
                update(model.Credit).where(model.Credit.id == credit_id).values(
                    remaining_debt=model.Credit.remaining_debt - amount))
            await session.commit()


async def credit_debt_accrual(credit_id: int, amount: float):
    async with async_session() as session:
        await session.execute(
            update(model.Credit).where(model.Credit.id == credit_id).values(remaining_debt=amount))
        await session.commit()
