from fastapi import APIRouter

from models.redis_connector import RedisConnector

router = APIRouter(prefix="/redis", tags=["Redis"])

redis = RedisConnector()


@router.post("/get_user_lang")
async def get_user_lang(user_id: str | int = None, all_dict: bool = False) -> str | dict:
    return await redis.get_user_lang(user_id=user_id, all_dict=all_dict)


@router.post("/update_user_lang")
async def update_user_lang(user_id: str | int, lang: str):
    return await redis.update_user_lang(user_id=user_id, lang=lang)


@router.post("/get_user_text")
async def get_user_text(user_id: str | int, module: str, handler: str, obj: str = "text") -> str:
    return await redis.get_user_text(user_id=user_id, module=module, handler=handler, obj=obj)


@router.post("/update_text")
async def update_text(lang: str, module: str, handler: str, text_data: dict):
    return await redis.update_text(lang=lang, module=module, handler=handler, text_data=text_data)
