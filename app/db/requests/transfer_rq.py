import app.db.models as model

from sqlalchemy import update

from app.db.requests.base_rq import async_session


async def transfer(sender_tg_id: int, recipient_tg_id: int, amount: float):
    async with async_session() as session:
        await session.execute(
            update(model.User).where(model.User.id == sender_tg_id).values(balance=model.User.balance - amount)
        )

        await session.execute(
            update(model.User).where(model.User.id == recipient_tg_id).values(balance=model.User.balance + amount)
        )

        await session.commit()
