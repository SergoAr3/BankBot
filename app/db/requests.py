import random

from app.db.models import async_session
from app.db.models import User, Transaction, TransactionType, CatImage, UserCat, Channel, ChannelSubscription
from sqlalchemy import select, func
from loguru import logger
import asyncio

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


async def get_user_balance(tg_user_id: int):
    async with async_session() as session:
        balance = await session.scalar(select(User.balance).where(User.telegram_user_id == tg_user_id))

        return balance


async def get_channels(tg_user_id: int):
    try:
        async with async_session() as session:
            subscribed_channels = select(
                ChannelSubscription.channel_id).select_from(
                ChannelSubscription).join(
                User, User.id == ChannelSubscription.user_id).where(
                User.telegram_user_id == tg_user_id)

            available_channels = await session.execute(
                select(Channel)
                .where(Channel.id.not_in(subscribed_channels)).order_by(Channel.id)
            )
            available_channels = available_channels.scalars().all()

            return available_channels

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении списка каналов: {e}")
        return []


async def get_image_number(tg_user_id: int, session):
    async with session:
        try:

            image_count = await session.scalar(select(func.count(CatImage.id)))

            image_numbers = list(range(1, image_count))

            user_purchased_images = await session.scalars(select(UserCat.cat_image_id)
                                                          .select_from(CatImage)
                                                          .join(UserCat, CatImage.id == UserCat.cat_image_id)
                                                          .join(User, UserCat.user_id == User.id)
                                                          .where(User.telegram_user_id == tg_user_id)
                                                          )

            user_purchased_images = set(user_purchased_images.all())

            user_available_images = [num for num in image_numbers if num not in user_purchased_images]

            if user_available_images:
                image_id = random.choice(user_available_images)

            return image_id
        except  SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при получении номера изображения: {e}")


async def get_image(tg_user_id: int):
    async with async_session() as session:
        try:
            image_id = await get_image_number(tg_user_id, session)

            image = await session.scalar(select(CatImage).where(CatImage.id == image_id))

            return image
        except  SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при получении изображения: {e}")


async def add_user(username: str, tg_user_id: int = None) -> None:
    async with async_session() as session:
        user_id = await session.scalar(select(User.telegram_user_id).where(User.telegram_user_id == tg_user_id))
        if not user_id:
            session.add(User(telegram_user_id=tg_user_id, username=username))
            await session.commit()


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


async def add_cat_buying_info(user_id: int, cat_image_id: int):
    async with async_session() as session:
        session.add(UserCat(user_id=user_id, cat_image_id=cat_image_id))
        await session.commit()


async def change_user_balance(tg_user_id: int, amount: int):
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.telegram_user_id == tg_user_id)
        )

        user = user.scalar_one_or_none()

        user.balance += amount
        await session.commit()


async def add_channel_subscription_info(user_id: int, channel_id: int):
    async with async_session() as session:
        session.add(ChannelSubscription(channel_id=channel_id, user_id=user_id))
        await session.commit()
