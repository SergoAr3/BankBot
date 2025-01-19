from app.db.models import async_session
from app.db.models import User, Transaction, TransactionType
from sqlalchemy import select
from loguru import logger

from sqlalchemy.exc import SQLAlchemyError


async def get_user(tg_user_id: int = None, username: str = None):
    try:
        async with async_session() as session:
            if tg_user_id:
                user = await session.execute(
                    select(User).where(User.telegram_user_id == tg_user_id)
                )

                user = user.scalar_one_or_none()

                return user
            else:
                user = await session.execute(
                    select(User).where(User.username == username)
                )
                user = user.scalar_one_or_none()

                return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении пользователя с tg_user_id={tg_user_id}: {e}")
        return None


async def get_user_id(tg_user_id: int = None, username: str = None):
    try:
        async with async_session() as session:
            if tg_user_id:
                user = await session.execute(
                    select(User.id).where(User.telegram_user_id == tg_user_id)
                )
                user = user.scalar_one_or_none()
                return user
            else:
                user = await session.execute(
                    select(User.id).where(User.username == username)
                )
                user = user.scalar_one_or_none()

                return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении пользователя с tg_user_id={tg_user_id}: {e}")
        return None


async def get_user_tg_id(tg_user_id: int = None, username: str = None):
    try:
        async with async_session() as session:
            if tg_user_id:
                user = await session.execute(
                    select(User.telegram_user_id).where(User.telegram_user_id == tg_user_id)
                )
                user = user.scalar_one_or_none()
                return user
            else:
                user = await session.execute(
                    select(User.telegram_user_id).where(User.username == username)
                )
                user = user.scalar_one_or_none()

                return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении пользователя с tg_user_id={tg_user_id}: {e}")
        return None


async def add_user(username: str, tg_user_id: int = None) -> None:
    async with async_session() as session:
        user_id = await session.scalar(select(User.telegram_user_id).where(User.telegram_user_id == tg_user_id))
        if not user_id:
            session.add(User(telegram_user_id=tg_user_id, username=username))
            await session.commit()


async def get_user_balance(tg_user_id: int):
    async with async_session() as session:
        balance = await session.scalar(select(User.balance).where(User.telegram_user_id == tg_user_id))

        return balance


async def transfer(sender_tg_id: int, recipient_tg_id: int, amount: int):
    async with async_session() as session:
        try:

            sender = await session.execute(
                select(User).where(User.telegram_user_id == sender_tg_id)
            )

            recipient = await session.execute(
                select(User).where(User.telegram_user_id == recipient_tg_id)
            )

            sender = sender.scalar_one_or_none()
            recipient = recipient.scalar_one_or_none()

            sender.balance -= amount
            recipient.balance += amount

            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при получении переводе монет: {e}")


async def add_transaction(user_id: int, amount: int, type: TransactionType, description: int = None):
    async with async_session() as session:
        try:

            session.add(Transaction(user_id=user_id, amount=amount, type=type, description=description))
            await session.commit()
        except  SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при записи транзакции: {e}")
