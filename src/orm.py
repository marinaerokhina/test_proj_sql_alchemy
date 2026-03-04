from sqlalchemy import text, insert, select, func, cast, Integer, and_
from sqlalchemy.orm import aliased, joinedload, selectinload
from src.database import sync_engine, async_engine, session_factory, async_session_factory, Base
from models import WorkersOrm, CVOrm, WorkLoad  # metadata_obj,

class SyncORM:
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_data():
        with session_factory() as session:
            worker_bobr = WorkersOrm(username="Bobr")
 #          session.add(worker_bobr)
            worker_volk = WorkersOrm(username="Volk")
 #          session.add(worker_volk)
            worker_koshk = WorkersOrm(username="Koshk")
 #          session.add(worker_koshk)
            session.add_all([worker_bobr, worker_volk, worker_koshk])
            session.flush() # - команда отправляет все изменения в бд, при этом не завершая запрос/сессию
            session.commit()

    @staticmethod
    def select_workers():
        with session_factory() as session:
            # worker_id = 1
            # worker = session.get(WorkersOrm, worker_id) #- только один результат
            query = select(WorkersOrm)  # select * from workers
            result = session.execute(query)
            #workers = result.all() - плохой вывод, человеко-не-интерпретируемый, кортежи
            #workers = result.scalars().all() - вывод первого значения в кортеже, но тоже человеко-не-интерпретируемый
            workers = result.scalars().all()
            print(f"{workers=}")


    @staticmethod
    def update_workers(worker_id: int = 2, new_username: str = "Daniel"):
        with session_factory() as session:
            worker = session.get(WorkersOrm, worker_id)
            worker.username = new_username
            #session.expire(worker) # или expire_all() - отменяет все изменения объекта, запрос в базу не отправляет, СИНХРОННАЯ ОПЕРАЦИЯ
            session.refresh(worker) # - обновление данных из бд в случае их изменения по сравнению с предыдущим их запросом
            session.commit()
            # минус такого подхода - больше запросов к базе, чем в core-стиле. В core - 1 запрос, здесь - 2 запроса

    @staticmethod
    def insert_cvs():
        with session_factory() as session:
            cv_worker1_1 = CVOrm(
                title="Python Junior Developer", salary=50000, work_load=WorkLoad.full_time, worker_id=1)
            cv_worker1_2 = CVOrm(
                title="Python Developer", salary=150000, work_load=WorkLoad.full_time, worker_id=1)
            cv_worker2_1 = CVOrm(
                title="Python Data Engineer", salary=250000, work_load=WorkLoad.part_time, worker_id=2)
            cv_worker2_2 = CVOrm(
                title="Data Scientist", salary=300000, work_load=WorkLoad.full_time, worker_id=2)
            session.add_all([cv_worker1_1, cv_worker1_2,
                             cv_worker2_1, cv_worker2_2])
            session.commit()

    @staticmethod
    def select_cvs_avg_salary(like_language: str = "Python"):
        with session_factory() as session:
            query = (
                select(
                    CVOrm.work_load,
                    cast(func.avg(CVOrm.salary), Integer).label("avg_salary"),
                )
                .select_from(CVOrm)
                .filter(and_(
                    CVOrm.title.contains(like_language),
                    CVOrm.salary > 40000,
                ))
                .group_by(CVOrm.work_load)
                .having(cast(func.avg(CVOrm.salary), Integer).label("avg_salary") > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            result = session.execute(query)
            res = result.all()
            print(res, res[0].avg_salary)


    @staticmethod
    def join_cte_subquery_window_func(like_language: str = "Python"):
        """
           WITH helper2 AS (
                 SELECT *, compensation-avg_workload_compensation AS compensation_diff
                 FROM
                 (SELECT
                     w.id,
                     w.username,
                     r.compensation,
                     r.workload,
                     avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
                 FROM resumes r
                 JOIN workers w ON r.worker_id = w.id) helper1
           )
           SELECT * FROM helper2
           ORDER BY compensation_diff DESC;
        """
        with session_factory() as session:
            c = aliased(CVOrm)
            w = aliased(WorkersOrm)
            Subq = (
                select(
                    c,
                    w,
                    func.avg(c.salary).over(partition_by=c.work_load).cast(Integer).label("avg_workload_salary"),
                )
                # .select_from(c)
                .join(w, c.worker_id == w.id).subquery("helper1")
                    #full=True, isouter = True - FULL JOIN + LEFT JOIN. RIGHT JOIN отсутствует в sqlalchemy
            )
            cte = (
                select(
                    #Subq.c.id, - айдишник итого был взят с cv's, а не с воркеров
                    Subq.c.worker_id,
                    Subq.c.username,
                    Subq.c.salary,
                    Subq.c.work_load,
                    Subq.c.avg_workload_salary,
                    (Subq.c.salary - Subq.c.avg_workload_compensation).label("salary_diff")
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.salary_diff.desc())
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all()
            print(f"{result=}")


    @staticmethod
    def select_workers_with_lazy_relationship():
        # ленивая подгрузка - сами мы запросы не делаем, подгружает система при вызове поля
        # но при этом во время подгрузки совершаеттся столько запросов, сколько работников подгружается
        # занимает время, память, эффективность низкая
        with session_factory() as session:
            query = (
                select(WorkersOrm)
            )
            res = session.execute(query)
            result = res.scalars().all() # конвертируем полученную информацию к формату модели
            w1_cv = result[0].cvs
            w2_cv = result[1].cvs
            print(w1_cv, w2_cv)


    @staticmethod
    def select_workers_with_joined_relationship():
        with session_factory() as session:
            query = (
                select(WorkersOrm)
                .option(joinedload(WorkersOrm.cvs)) # join резюме сразу - один огромный запрос со всеми данными
            )
            # и никаких доп запросов после этого - вся информация уже подгружена
            # оптимизация времени работы, каналов доступа
            # получается вложенная структура данных
            res = session.execute(query)
            result = res.unique().scalars().all() # конвертируем полученную информацию к формату модели
            #запрос на уникальность делается на уровне алхимии, чтобы отсеять повторяющиеся первичные ключи
            w1_cv = result[0].cvs
            w2_cv = result[1].cvs
            print(w1_cv, w2_cv)
            # проблема - дублирование данных (особенно чувствительно при дублировании первичных ключей)
            # связь 1 - ко - многим -> много лишних данных выгружается
            # joinedload подходит для связей многие - к - 1 и 1 - к - 1

    @staticmethod
    def select_workers_with_selectin_relationship():
        with session_factory() as session:
            query = (
                select(WorkersOrm)
                .option(selectinload(WorkersOrm.cvs))
            )
            # метод сначала выбрал всех существующих работников, а потом подгрузил только их резюме
            # при параметризованном выборе (т.е. выбираются не все строки, а часть по определенным критериям),
            # то резюме подгружаются только для выбранных первым запросом работников.
            # по сути, сразу производится проверка на уникальность загружаемых данных
            # очень хорошо подходит для подгрузки данных, связанных связью 1 - ко - многим
            res = session.execute(query)
            result = res.unique().scalars().all()
            w1_cv = result[0].cvs # костыльная печать данных
            w2_cv = result[1].cvs
            print(w1_cv, w2_cv)





class AsyncORM:
    # Асинхронный вариант, не показанный в видео
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


    @staticmethod
    async def insert_data():
        async with async_session_factory() as session:
            worker_bobr = WorkersOrm(username="Bobr")
            worker_volk = WorkersOrm(username="Volk")
            worker_koshk = WorkersOrm(username="Koshk")
            session.add_all([worker_bobr, worker_volk, worker_koshk])
            await session.commit()

    @staticmethod
    async def select_workers():
        async with async_session_factory() as session:
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        async with async_session_factory() as session:
            worker_michael = await session.get(WorkersOrm, worker_id)
            worker_michael.username = new_username
            await session.refresh(worker_michael)
            await session.commit()

    # ВНИМАНИЕ
    # в асинхронной алхимии НЕЛЬЗЯ использовать ленивую подгрузку
    # она вызывает ошибки - алхимия не может вызвать асинхронный код когда-нибудь потом, когда захотелось
    # в таком случае все связи подгружают СРАЗУ - через options + joinedload/selectinload
