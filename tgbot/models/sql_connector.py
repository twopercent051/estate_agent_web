from typing import List

from sqlalchemy import MetaData, Column, Integer, String, select, insert, delete, TEXT, update, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker, as_declarative
from sqlalchemy.sql import expression

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()


class UtcNow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(UtcNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class FilesDB(Base):
    __tablename__ = "files"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    file_id = Column(String, nullable=False)
    file_name = Column(String, nullable=False)


class UsersDB(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    create_dtime = Column(DateTime, nullable=False, server_default=UtcNow())
    request_count = Column(Integer, nullable=False, server_default="0")


class TextsDB(Base):
    __tablename__ = "texts"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    chapter = Column(String, nullable=False)
    text = Column(TEXT, nullable=False)


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
            query = select(cls.model.__table__.columns).filter(cls.model.file_name.like(f"%{keyword}%")). \
                order_by(cls.model.id.asc())
            result = await session.execute(query)
            return result.mappings().all()


class TextsDAO(BaseDAO):
    model = TextsDB

    @classmethod
    async def get_text(cls, chapter: str):
        text = await cls.get_one_or_none(chapter=chapter)
        if text:
            return text["text"]
        else:
            return "ТЕКСТ НЕ ЗАДАН"

    @classmethod
    async def update_by_chapter(cls, chapter: str, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(chapter=chapter)
            await session.execute(stmt)
            await session.commit()


class UsersDAO(BaseDAO):
    model = UsersDB

    @classmethod
    async def update_requests(cls, user_id: str):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(request_count=cls.model.request_count + 1).filter_by(user_id=user_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_order_by_count(cls) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).order_by(cls.model.request_count.desc())
            result = await session.execute(query)
            return result.mappings().all()
