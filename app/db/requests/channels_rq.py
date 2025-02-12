import app.db.models as model

from sqlalchemy import select

from app.db.requests.base_rq import async_session



async def get_channels(user_id: int):
    async with async_session() as session:
        subscribed_channels = select(
            model.ChannelSubscription.channel_id).select_from(
            model.ChannelSubscription).join(
            model.User, model.User.id == model.ChannelSubscription.user_id).where(
            model.User.id == user_id)

        available_channels = await session.execute(
            select(model.Channel)
            .where(model.Channel.id.not_in(subscribed_channels)).order_by(model.Channel.id)
        )
        available_channels = available_channels.scalars().all()

        return available_channels


async def add_channel_subscription_info(user_id: int, channel_id: int):
    async with async_session() as session:
        session.add(model.ChannelSubscription(channel_id=channel_id, user_id=user_id))
        await session.commit()
