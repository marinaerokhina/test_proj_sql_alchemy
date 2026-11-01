import datetime
from typing import Optional, Annotated
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func, text
from src.database import Base, str_255
from sqlalchemy.orm import Mapped, mapped_column, relationship
import  enum

# хранит в себе данные о всех таблицах на стороне приложения
# передается в таблицы и модели для, например, миграций
metadata_obj = MetaData()

workers_table = Table(
     "workers",
     metadata_obj,
     Column("id", Integer, primary_key=True),
     Column("username", String),
)

# модель таблицы:
# employees_table = Table(
#     "employees",
#     metadata_obj,
#     Column("id", Integer, primary_key=True),
#     Column("name", String),
# )
#это был императивный стиль

#а это - декларативный
# Классы, в которых хранятся метаданные
# теперь все хранится в Base, metadata_obj теперь не нужна

#переиспользуем переменную, чтобы каждый раз не писать одно и то же
intpk = Annotated[int, mapped_column(primary_key=True)]
CreatedAt = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
UpdatedAt = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate= datetime.datetime.utcnow)]

class WorkersOrm(Base):
    __tablename__ = "workers"
    #id: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[intpk]
    username: Mapped[str]# = mapped_column()

    cvs: Mapped[list["CVOrm"]] = relationship(
        back_populates="worker",
        #backref = "worker" - неявное указание на связь. Создает в указанной для связывания модели поле, непосредственно
        # непосредлственно связывающее две модели
        # устаревшая методика, не стоит использовать

    )

    cvs_part_time: Mapped[list["CVOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == CVOrm.worker_id, CVOrm.work_load == 'part_time')",
        viewonly=True,  # Filtered relationship; managed through WorkersOrm.cvs
        # join для упрощенной выборки через отношения
    )

class WorkLoad(enum.Enum):
    part_time = "part_time"
    full_time = 'full_time'

class CVOrm(Base):
    __tablename__ = "cvs"
    #id: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[intpk]
    #title: Mapped[str] = mapped_column(String(255))
    title: Mapped[str_255]
    #salary: Mapped[int] = mapped_column(nullable = True)
    #salary: Mapped[Optional[int]]
    salary: Mapped[int | None]
    work_load: Mapped[WorkLoad]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete ="CASCADE")) #- рекомендуется
    #но есть другой вариант: mapped_column(ForeignKey(WorkersOrm.id)) - у него есть свои проблемы, вроде цикличности
    #или разнесения моделей по разным файлам и вследствие проблемы с доступом
    #created_at = Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    #func.now() - время по местному часовому поясу
    #created_at: Mapped[datetime.datetime] = mapped_column(default=text("TIMEZONE('utc', now())")) - это со стороны приложения отправка
    #updated_at: Mapped[datetime.datetime] = mapped_column(
        #server_default=text("TIMEZONE('utc', now())"), onupdate= datetime.datetime.utcnow)
    # пока заглушка, лучше через триггеры
    #datetime.datetime.now()) - через орм, не всегда эффективен и выполняется
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    worker: Mapped["WorkersOrm"] = relationship(
        back_populates= "cvs" # ссылка на поле другой модели, явное указание на то, что модели связаны
    )
    # в кавычках лучше чем без кавычек, иначе появляются проблемы с циклическими импортами

    # выглядит красиво, но удобно только тогда, когда мало моделей и они не очень масштабные
    # def __repr__(self):
    #     return f"<CV:\n id = {self.id},\n title = {self.title}>"