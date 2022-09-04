import os
import logging
import aioredis

from fastapi import status, HTTPException

from services.CacheAbstract import CacheAbstract


log = logging.getLogger("API_LOG")


class RedisHandler(CacheAbstract):
    def __init__(self):
        try:
            self.conn = aioredis.Redis(host=os.getenv("REDIS_HOST", "cache"),
                                       port=int(os.getenv("REDIS_PORT", "6379")),)
        except Exception as err:
            log.error(f"Error occured: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Exception occured : {err}",
            ) from err

    async def get_key(self, key):
        try:
            return await self.conn.get(key)
        except Exception as err:
            log.error(f"Error occured: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Exception occured : {err}",
            ) from err

    async def set_key(self, key, value, ttl=None):
        try:
            await self.conn.set(key, value)
            await self.conn.expire(key, ttl)
            return True
        except Exception as err:
            log.error(f"Error occured: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Exception occured : {err}",
            ) from err
