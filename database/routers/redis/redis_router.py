import logging

from fastapi import APIRouter

from create_app import logger
from models.redis_connector import ModelRedisConnector

# from api_models.redis_connector import RedisConnector

router = APIRouter(prefix="/redis", tags=["Redis"])


@router.post("/get_user_lang")
async def get_user_lang(user_id: str | int = None, all_dict: bool = False) -> str | dict:
    return await ModelRedisConnector.get_user_lang(user_id=user_id, all_dict=all_dict)


@router.post("/update_user_lang")
async def update_user_lang(user_id: str | int, lang: str):
    return await ModelRedisConnector.update_user_lang(user_id=user_id, lang=lang)


@router.post("/get_text_by_lang")
async def get_text_by_lang(lang: str, module: str, handler: str, obj: str = "text"):
    return await ModelRedisConnector.get_text_by_lang(lang=lang, module=module, handler=handler, obj=obj)


@router.post("/get_user_text")
async def get_user_text(user_id: str | int, module: str, handler: str, obj: str = "text") -> str:
    return await ModelRedisConnector.get_user_text(user_id=user_id, module=module, handler=handler, obj=obj)


@router.post("/update_text")
async def update_text(lang: str, module: str, handler: str, obj: str, text: str):
    return await ModelRedisConnector.update_text(lang=lang, module=module, handler=handler, obj=obj, text=text)


@router.post("/get_tlg_code")
async def get_tlg_code() -> dict:
    resp = await ModelRedisConnector.get_tlg_code()
    logger.info(resp)
    return dict(code=resp)


@router.post("/set_tlg_code")
async def set_tlg_code(code: str):
    return await ModelRedisConnector.set_tlg_code(code=code)
