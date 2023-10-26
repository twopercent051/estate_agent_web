from typing import List

from fastapi import APIRouter

from models.sql_connector import ModelsUsersDAO

router = APIRouter(prefix="/sql_files", tags=["Files"])

model = ModelsUsersDAO


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


@router.post("/create_many")
async def create_many(files: List[dict]):
    return await model.create_many(files=files)


@router.post("/get_many_by_keyword")
async def get_many_by_keyword(keyword: str) -> List[dict]:
    return await model.get_many_by_keyword(keyword=keyword)


@router.post("/update_many")
async def update_many(files: List[dict]):
    return await model.update_many(files=files)
