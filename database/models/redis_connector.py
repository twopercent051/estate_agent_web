import json

import redis
import aioredis

from create_app import config, logger


class RedisConnector:

    redis = aioredis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.database)
    user_lang_db = "user_lang"
    texts_db = "texts"

    # def __init__(self):
    #     # self.r = redis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.database)
    #     self.user_lang_db = "user_lang"
    #     self.texts_db = "texts"

    @classmethod
    async def redis_start(cls):
        for db in [cls.user_lang_db, cls.texts_db]:
            response = await cls.redis.get(db)
            if not response:
                await cls.redis.set(db, json.dumps(dict()))
        logger.info('Redis connected OKK')

    @classmethod
    async def get_user_lang(cls, user_id: str | int = None, all_dict: bool = False) -> str | dict:
        response = await cls.redis.get(cls.user_lang_db)
        if not response:
            return
        response = json.loads(response)
        if all_dict:
            return response
        return response.get(str(user_id), "en")

    @classmethod
    async def update_user_lang(cls, user_id: str | int, lang: str):
        data = await cls.get_user_lang(all_dict=True)
        data[str(user_id)] = lang
        await cls.redis.set(cls.user_lang_db, json.dumps(data))

    @classmethod
    async def get_user_text(cls, user_id: str | int, module: str, handler: str, obj: str = "text") -> str:
        user_lang = await cls.get_user_lang(user_id=user_id)
        texts_data = json.loads(await cls.redis.get(cls.texts_db))
        no_text = "ТЕКСТ НЕ ЗАДАН"
        try:
            if obj == "text":
                return texts_data[user_lang][module][handler][obj]
            else:
                return texts_data[user_lang][module][handler]["buttons"][obj]
        except KeyError:
            return no_text

    @classmethod
    async def update_text(cls, lang: str, module: str, handler: str, text_data: dict):
        data = await cls.redis.get(cls.texts_db)
        data = json.loads(data)
        data[lang][module][handler] = text_data
        await cls.redis.set(cls.user_lang_db, json.dumps(data))


def test():
    red = RedisConnector()
    red.redis_start()


if __name__ == "__main__":
    test()
