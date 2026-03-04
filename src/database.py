import asyncio
from typing import Annotated

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import URL, text, create_engine, String
from src.config import settings

# from src.core import get_123_async

# Создаем движок для подключения к бд с синхр подключением
sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False,
    # pool_size=5,
    # max_overflow=10,
)

# def get_123():
#    with sync_engine.connect() as conn:
#        res = conn.execute(text("SELECT 1,2,3"))
#        print(f"{res.all()=}") - перенесен в core.py


# асинхронный движок
async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False,
    # pool_size=5,
    # max_overflow=10,
)

# async def get_123_async():
#    async with async_engine.connect() as conn:
#        res = await conn.execute(text("SELECT 1,2,3"))
#        print(f"{res.all()=}") - перенесен в core.py

# asyncio.run(get_123_async())

# session = транзакция
# with Session(sync_engine) as session:
#     session.


# sessionmaker = фабрика sessions
session_factory = sessionmaker(sync_engine)
# переиспользуем экземпляр
# with session() as session:
#     ...

# асинхронный формат
async_session_factory = async_sessionmaker(async_engine)
# аналогично контестный менеджер
# async with async_session() as a_session:
#     await a_session...

str_255 = Annotated[str, 255]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_255: String(255)
    }

    # переопределяем стандартным метод для удобной печати данных
    # def __repr__(self):
    #   return f"<{self.__class__.__name__}>" - пример
    # базовая версия
    # def __repr__(self):
    #     cols = []
    #     for col in self.__table__.columns.keys():
    #         cols.append(f"{col} = {getattr(self, col)}")
    #     return f"<{self.__class__.__name__} {',\n'.join(cols)}>"

    # продвинутая версия: кастомизация через прописывание параметров для конкретной модели и не более
    repr_cols_num = 3
    repr_cols = tuple()
    # вот эти параметры выше и прописываются в моделях
    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"