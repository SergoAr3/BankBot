import random

import app.db.models as model

from sqlalchemy import select, func

from app.db.requests.base_rq import async_session


async def get_image_number(user_id: int, session):
    async with session:
        image_count = await session.scalar(select(func.count(model.CatImage.id)))

        image_numbers = list(range(1, image_count + 1))

        user_purchased_images = await session.scalars(select(model.UserCat.cat_image_id)
                                                      .select_from(model.CatImage)
                                                      .join(model.UserCat,
                                                            model.CatImage.id == model.UserCat.cat_image_id)
                                                      .join(model.User, model.UserCat.user_id == model.User.id)
                                                      .where(model.User.id == user_id)
                                                      )

        user_purchased_images = set(user_purchased_images.all())

        user_available_images = [num for num in image_numbers if num not in user_purchased_images]

        if user_available_images:
            image_id = random.choice(user_available_images)

            return image_id
        return None


async def get_image(user_id: int):
    async with async_session() as session:
        image_id = await get_image_number(user_id, session)

        if image_id:
            image = await session.scalar(select(model.CatImage).where(model.CatImage.id == image_id))

            return image
        return None


async def add_cat_buying_info(user_id: int, cat_image_id: int):
    async with async_session() as session:
        session.add(model.UserCat(user_id=user_id, cat_image_id=cat_image_id))
        await session.commit()
