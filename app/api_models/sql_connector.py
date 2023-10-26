from typing import List, Optional

import aiohttp

from create_app import DB_URL


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = ""

    @classmethod
    async def _post_request(cls, route: str, **data):
        url = f"{DB_URL}/{cls.model}/{route}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=data) as resp:
                return await resp.json()

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> Optional[dict]:
        return await cls._post_request(route="get_one", **filter_by)

    @classmethod
    async def get_many(cls, **filter_by) -> List[dict]:
        return await cls._post_request(route="get_many", **filter_by)

    @classmethod
    async def create(cls, **data):
        return await cls._post_request(route="create", **data)

    @classmethod
    async def delete(cls, **data):
        return await cls._post_request(route="delete", **data)


class FilesDAO(BaseDAO):
    model = "sql_files"

    @classmethod
    async def create_many(cls, files: List[dict]):
        return await cls._post_request(route="create_many", files=files)

    @classmethod
    async def get_many_by_keyword(cls, keyword: str) -> List[dict]:
        return await cls._post_request(route="get_many_by_keyword", keyword=keyword)

    @classmethod
    async def update_many(cls, files: List[dict]) -> int:
        return await cls._post_request(route="update_many", files=files)


class UsersDAO(BaseDAO):
    model = "sql_users"

    @classmethod
    async def update_requests(cls, user_id: str):
        return await cls._post_request(route="update_requests", user_id=user_id)

    @classmethod
    async def update_calculation(cls, user_id: str):
        return await cls._post_request(route="update_calculation", user_id=user_id)

    @classmethod
    async def update_telegraph_count(cls, user_id: str):
        return await cls._post_request(route="update_telegraph_count", user_id=user_id)

    @classmethod
    async def get_order_by_count(cls) -> List[dict]:
        return await cls._post_request(route="get_order_by_count")

    @classmethod
    async def update_by_user_id(cls, user_id: str, **data):
        return await cls._post_request(route="update_by_user_id", user_id=user_id, **data)

    @classmethod
    async def get_users_for_mailing(cls, data: dict):
        return await cls._post_request(route="get_users_for_mailing", data=data)
