from typing import List

from sqlalchemy import MetaData, Column, Integer, String, select, insert, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, as_declarative

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()


class FilesDB(Base):
    __tablename__ = "files"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    file_id = Column(String, nullable=False)
    file_name = Column(String, nullable=False)


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = None

    @classmethod
    async def get_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by).limit(1)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_many(cls, **filter_by) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by).order_by(cls.model.id.asc())
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete(cls, **data):
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter_by(**data)
            await session.execute(stmt)
            await session.commit()


class FilesDAO(BaseDAO):
    model = FilesDB

    @classmethod
    async def create_many(cls, files: List[dict]):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(files)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_many_by_keyword(cls, keyword: str) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter(cls.model.file_name.like(f"%{keyword}%")).order_by(cls.model.id.asc())
            result = await session.execute(query)
            return result.mappings().all()
