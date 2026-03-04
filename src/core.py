from sqlalchemy import text, insert, select, update
from src.database import async_engine, sync_engine
from src.models import metadata_obj, workers_table



# Простой запрос к бд (и подключение) с помощью контекстного менеджера БЕЗ СОХРАНЕНИЯ
# с сохранением - begin()/conn.commit() в connect()
def get_123():
    with sync_engine.connect() as conn:
        res = conn.execute(text("SELECT 1,2,3"))
        print(f"{res.all()=}")

async def get_123_async():
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1,2,3"))
        print(f"{res.all()=}")


class SyncCore:
# один из вариантов создания таблиц
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

# к обоим методам можно добавить @staticmethod и обернуть в класс SyncCore

# один из вариантов заполнения таблиц
    @staticmethod
    def insert_data():
        with sync_engine.connect() as conn:
         # statement = """insert into workers (username) values ('AO Bobr'),
         # ('OOO Volk');""" - неудобно и долго (хотя под капотом быстрее)
         # через query builder
            statement = insert(workers_table).values(
                [
                    {"name": "AO Bobr"},
                    {"name": "OOO Volk"}
                ]
            )
            conn.execute(statement)
            conn.commit()

    @staticmethod
    def select_workers():
        with sync_engine.connect() as conn:
            query = select(workers_table) # select * from workers
            result = conn.execute(query)
            workers = result.all()
            print(f"{workers=}")


    @staticmethod
    def update_workers(worker_id: int = 2, new_username: str = "Daniel"):
        with sync_engine.connect() as conn:
            # statement = text("UPDATE workers SET username=:new_username"
            #                  "WHERE id=:id")
            # statement = statement.bindparams(username=new_username, id=worker_id) - защита от sql-инъекций
            statement = (
                update(workers_table)
                .values(username=new_username)
                #.where(workers_table.c.id==worker_id) - долго и неудобно писать
                .filter_by(id=worker_id)

            )
            conn.execute(statement)
            conn.commit()


class AsyncCore:
    # Асинхронный вариант, не показанный в видео
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata_obj.drop_all)
            await conn.run_sync(metadata_obj.create_all)


    @staticmethod
    async def insert_workers():
        async with async_engine.connect() as conn:
            stmt = insert(workers_table).values(
                [
                    {"username": "Bobr"},
                    {"username": "Volk"},
                ]
            )
            await conn.execute(stmt)
            await conn.commit()

    @staticmethod
    async def select_workers():
        async with async_engine.connect() as conn:
            query = select(workers_table) # SELECT * FROM workers
            result = await conn.execute(query)
            workers = result.all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        async with async_engine.connect() as conn:
            # stmt = text("UPDATE workers SET username=:username WHERE id=:id")
            # stmt = stmt.bindparams(username=new_username, id=worker_id)
            stmt = (
                update(workers_table)
                .values(username=new_username)
                # .where(workers_table.c.id==worker_id)
                .filter_by(id=worker_id)
            )
            await conn.execute(stmt)
            await conn.commit()