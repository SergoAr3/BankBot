from datetime import datetime, timedelta

from loguru import logger

from config import RedisConfig

import redis.asyncio as aioredis

pool = aioredis.ConnectionPool.from_url(RedisConfig.get_connection())
redis_client = aioredis.Redis(connection_pool=pool)


async def get_cooldown(user_id):
    async with redis_client as client:
        res = await client.get(f"cooldown:check_subscriptions:{user_id}")
        return res


async def set_cooldown(user_id, cooldown_seconds, current_time):
    async with redis_client as client:
        return await client.setex(f"cooldown:check_subscriptions:{user_id}", cooldown_seconds, current_time)

