# test_proj_sql_alchemy — Изучение SQLAlchemy ORM

Учебный проект, созданный по бесплатному видеокурсу SQLAlchemy Артема Шумейко. Демонстрирует работу с реляционными базами данных через ORM SQLAlchemy 2.0, включая синхронный и асинхронный подходы, сложные запросы, relationships и оптимизацию загрузки данных.

## 🎯 Цель проекта

Практическое изучение возможностей SQLAlchemy:
- Создание моделей с relationships (один-ко-многим)
- Синхронный и асинхронный режимы работы
- CRUD операции через ORM
- Сложные SQL-запросы: JOIN, CTE, подзапросы, оконные функции
- Агрегатные функции и группировка
- Оптимизация загрузки связанных данных (lazy, joined, selectin)

## 📁 Структура проекта

```
test_proj_sql_alchemy/
├── src/
│   ├── config.py          # Конфигурация подключения к БД
│   ├── database.py        # Настройка движков и сессий
│   ├── models.py          # ORM модели (Workers, CV)
│   ├── orm.py             # CRUD операции и сложные запросы
│   ├── core.py            # Core-style запросы (альтернативный подход)
│   └── main.py            # Точка входа
├── .env                   # Переменные окружения (URL БД)
└── requirements.txt       # Зависимости
```

## 🗄 Схема базы данных

Проект использует две связанные таблицы:

```
workers (работники)
├── id (PK)
└── username

cvs (резюме)
├── id (PK)
├── title
├── salary
├── work_load (enum: part_time, full_time)
├── worker_id (FK → workers.id, CASCADE)
├── created_at (server_default: UTC timestamp)
└── updated_at (server_default + onupdate)
```

**Связь:** Один работник → много резюме (one-to-many)

## 🛠 Технологии

- **Python 3.10+**
- **SQLAlchemy 2.0** — ORM и Core
- **PostgreSQL** — реляционная база данных
- **psycopg2** — синхронный драйвер
- **asyncpg** — асинхронный драйвер
- **asyncio** — асинхронное программирование

## 🚀 Запуск

### Требования
- Python 3.10+
- PostgreSQL 12+
- Установленный PostgreSQL сервер

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка .env
Создайте файл `.env` с переменными:
```env
DATABASE_URL_psycopg=postgresql://user:password@localhost:5432/dbname
DATABASE_URL_asyncpg=postgresql+asyncpg://user:password@localhost:5432/dbname
```

### Запуск
```bash
python -m src.main
```

## 💡 Ключевые возможности

### 1. ORM модели с relationships

```python
class WorkersOrm(Base):
    __tablename__ = "workers"
    id: Mapped[intpk]
    username: Mapped[str]
    cvs: Mapped[list["CVOrm"]] = relationship(
        back_populates="worker"
    )
    cvs_part_time: Mapped[list["CVOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == CVOrm.worker_id, CVOrm.work_load = 'part_time')"
    )

class CVOrm(Base):
    __tablename__ = "cvs"
    id: Mapped[intpk]
    title: Mapped[str_255]
    salary: Mapped[int|None]
    work_load: Mapped[WorkLoad]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE"))
    worker: Mapped["WorkersOrm"] = relationship(back_populates="cvs")
```

### 2. CRUD операции

**Создание:**
```python
with session_factory() as session:
    worker = WorkersOrm(username="Bobr")
    session.add(worker)
    session.commit()
```

**Чтение:**
```python
query = select(WorkersOrm)
result = session.execute(query)
workers = result.scalars().all()
```

**Обновление:**
```python
worker = session.get(WorkersOrm, worker_id)
worker.username = "NewName"
session.refresh(worker)
session.commit()
```

### 3. Сложные запросы с агрегацией

```python
query = (
    select(
        CVOrm.work_load,
        cast(func.avg(CVOrm.salary), Integer).label("avg_salary"),
    )
    .select_from(CVOrm)
    .filter(and_(
        CVOrm.title.contains("Python"),
        CVOrm.salary > 40000,
    ))
    .group_by(CVOrm.work_load)
    .having(cast(func.avg(CVOrm.salary), Integer) > 70000)
)
```

### 4. JOIN, CTE, подзапросы и оконные функции

```python
# Оконная функция для расчета средней зарплаты по workload
Subq = (
    select(
        c, w,
        func.avg(c.salary).over(partition_by=c.work_load).cast(Integer).label("avg_workload_salary"),
    )
    .join(w, c.worker_id == w.id)
    .subquery("helper1")
)

# CTE (Common Table Expression)
cte = (
    select(
        Subq.c.worker_id,
        Subq.c.username,
        (Subq.c.salary - Subq.c.avg_workload_salary).label("salary_diff")
    )
    .cte("helper2")
)

query = select(cte).order_by(cte.c.salary_diff.desc())
```

### 5. Оптимизация загрузки relationships

**Lazy loading (по умолчанию):**
```python
# Делает N+1 запросов — неэффективно для больших данных
query = select(WorkersOrm)
result = session.execute(query).scalars().all()
w1_cv = result[0].cvs  # Дополнительный запрос при обращении
```

**Joined loading (JOIN):**
```python
# Один большой запрос с JOIN — хорошо для связей many-to-one, one-to-one
query = (
    select(WorkersOrm)
    .options(joinedload(WorkersOrm.cvs))
)
result = session.execute(query).unique().scalars().all()
```

**Selectin loading (подзапрос):**
```python
# Два запроса: сначала основные сущности, потом связанные — идеально для one-to-many
query = (
    select(WorkersOrm)
    .options(selectinload(WorkersOrm.cvs))
)
result = session.execute(query).unique().scalars().all()
```

### 6. Асинхронный режим

```python
class AsyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_data():
        async with async_session_factory() as session:
            worker = WorkersOrm(username="Bobr")
            session.add(worker)
            await session.commit()

    @staticmethod
    async def select_workers():
        async with async_session_factory() as session:
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
```

**Важно:** В асинхронном режиме нельзя использовать lazy loading — только joinedload/selectinload.

## 📚 Чему научилась

✅ SQLAlchemy ORM 2.0 (декларативный стиль)  
✅ Создание моделей с relationships (one-to-many)  
✅ Синхронный и асинхронный режимы работы  
✅ CRUD операции через ORM  
✅ Сложные SQL-запросы: JOIN, CTE, подзапросы  
✅ Оконные функции (OVER, PARTITION BY)  
✅ Агрегатные функции: AVG, COUNT, SUM  
✅ Группировка: GROUP BY, HAVING  
✅ Оптимизация загрузки: lazy, joined, selectin  
✅ Работа с enum типами  
✅ Server-side defaults (TIMEZONE, now())  
✅ Каскадное удаление (ON DELETE CASCADE)  
✅ Type annotations для моделей  
✅ Конфигурация через .env  

## 🔮 Возможные улучшения

- [ ] Добавить миграции через Alembic
- [ ] Реализовать CRUD API (FastAPI/Flask)
- [ ] Добавить валидацию данных (Pydantic)
- [ ] Покрыть тестами (pytest)
- [ ] Добавить логирование запросов
- [ ] Реализовать пагинацию
- [ ] Добавить кэширование
- [ ] Docker-контейнеризация

## 📝 Примечание

Проект создан в учебных целях для изучения SQLAlchemy. Код содержит подробные комментарии, объясняющие каждый аспект работы с ORM.

---

**Автор:** Марина Ерохина  
**Источник:** Видеокурс SQLAlchemy Артема Шумейко (Rutube)
