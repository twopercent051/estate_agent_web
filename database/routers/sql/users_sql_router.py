from fastapi import APIRouter

from models.sql_connector import UsersDAO

router = APIRouter(prefix="/sql_users", tags=["Users"])

model = UsersDAO


@router.post("/get_one")
async def get_one(data: dict) -> dict:
    return await model.get_one_or_none(**data)


@router.post("/get_many")
async def get_many(data: dict) -> list:
    return await model.get_many(**data)


@router.post("/create")
async def create(data: dict):
    return await model.create(**data)


@router.post("/delete")
async def create(data: dict):
    return await model.delete(**data)


@router.post("/update_requests")
async def update_requests(user_id: str):
    return await model.update_requests(user_id=str(user_id))


@router.post("/update_calculation")
async def update_calculation(user_id: str):
    return await model.update_calculation(user_id=str(user_id))


@router.post("/update_telegraph_count")
async def update_requests(user_id: str):
    return await model.create(user_id=str(user_id))


@router.post("/get_order_by_count")
async def get_order_by_count():
    return await model.get_order_by_count()


@router.post("/update_by_user_id")
async def update_by_user_id(user_id: str, **data):
    return await model.update_by_user_id(user_id=user_id, **data)
