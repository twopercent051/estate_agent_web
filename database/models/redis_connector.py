import json

import aioredis

from create_app import config, logger


class ModelRedisConnector:
    redis = aioredis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.database)
    user_lang_db = "user_lang"
    texts_db = "texts"
    telegram_auth_db = "telegram_auth"

    @classmethod
    async def redis_start(cls):
        for db in [cls.user_lang_db, cls.texts_db]:
            response = await cls.redis.get(db)
            if not response:
                await cls.redis.set(db, json.dumps(dict()))
        response = await cls.redis.get(cls.telegram_auth_db)
        if not response:
            await cls.redis.set(cls.telegram_auth_db, "")
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
    async def get_text_by_lang(cls, lang: str, module: str, handler: str, obj: str = "text") -> str:
        texts_data = json.loads(await cls.redis.get(cls.texts_db))
        no_text = "ТЕКСТ НЕ ЗАДАН"
        try:
            return texts_data[lang][module][handler][obj]
        except KeyError:
            return no_text

    @classmethod
    async def update_user_lang(cls, user_id: str | int, lang: str):
        data = await cls.get_user_lang(all_dict=True)
        data[str(user_id)] = lang
        await cls.redis.set(cls.user_lang_db, json.dumps(data))

    @classmethod
    async def get_user_text(cls, user_id: str | int, module: str, handler: str, obj: str = "text") -> str:
        user_lang = await cls.get_user_lang(user_id=user_id)
        return await cls.get_text_by_lang(lang=user_lang, module=module, handler=handler, obj=obj)

    @classmethod
    async def update_text(cls, lang: str, module: str, handler: str, obj: str, text: str):
        data = await cls.redis.get(cls.texts_db)
        data = json.loads(data)
        if lang not in data:
            data[lang] = {}
        if module not in data[lang]:
            data[lang][module] = {}
        if handler not in data[lang][module]:
            data[lang][module][handler] = {}
        if obj not in data[lang][module][handler]:
            data[lang][module][handler][obj] = {}
        data[lang][module][handler][obj] = text
        await cls.redis.set(cls.texts_db, json.dumps(data))

    @classmethod
    async def set_tlg_code(cls, code: str):
        await cls.redis.set(cls.telegram_auth_db, code, ex=300)

    @classmethod
    async def get_tlg_code(cls):
        return await cls.redis.get(cls.telegram_auth_db)
