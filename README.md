# SQLAlchemy ORM Practice

**Python · PostgreSQL · SQLAlchemy 2.x · AsyncIO**

A university-level practice repository exploring SQLAlchemy ORM and Core with PostgreSQL. It covers relational models, synchronous and asynchronous sessions, joins, aggregations, CTEs, window functions, and relationship-loading strategies.

> **Learning project:** Based on a free SQLAlchemy video course by Artem Shumeiko. This is an educational code laboratory, not a deployed web service or a production-ready API.

## Topics explored

| Area | Examples in the repository |
| --- | --- |
| Data modeling | `workers` and `cvs` entities, primary/foreign keys, enum types |
| CRUD | Create, read, update via ORM and SQLAlchemy Core |
| Advanced queries | JOIN, GROUP BY, HAVING, CTE, window functions |
| Relationships | One-to-many, lazy loading, joinedload, selectinload |
| Async database access | `asyncpg` driver, async sessions, `asyncio` |
| Schema handling | SQLAlchemy metadata-based table creation |

## Technology

- Python 3.10+
- PostgreSQL
- SQLAlchemy 2.x
- psycopg 3 (synchronous connection)
- asyncpg (asynchronous connection)
- pydantic-settings (local database configuration)

## Quick start

1. Install Python 3.10+ and PostgreSQL and start the PostgreSQL service.
2. Create a **local development database** named `sqlalchemy_practice` (or configure a different existing database name).
3. Clone the repository and create a virtual environment:

   ```bash
   git clone https://github.com/marinaerokhina/test_proj_sql_alchemy.git
   cd test_proj_sql_alchemy
   python -m venv .venv
   ```

4. Activate the environment: Windows PowerShell `.venv\Scripts\Activate.ps1`, or macOS/Linux `source .venv/bin/activate`.
5. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Copy `.env.example` to an untracked `.env` file and enter **your own PostgreSQL password** (do not commit the `.env` file).
7. Run one command at a time from the repository root:

   ```bash
   python -m src.main init
   python -m src.main seed
   python -m src.main list
   ```

`init` creates tables if they do not exist; `seed` adds three example workers; `list` prints the workers. Running `seed` again adds additional rows. **These commands do not delete existing tables.**

### Important notes

- This repository is an experiment playground with additional `SyncORM`, `AsyncORM`, `SyncCore`, and `AsyncCore` methods in `src/orm.py` and `src/core.py`. Not all exercises have been exercised together in a clean environment.
- Never point an educational database experiment at a production database. Some older learning functions depend on sample rows or fixed IDs.
- A working local PostgreSQL server and appropriate database permissions are necessary.
- A live integration test has not yet been run after these portfolio updates.

## Structure

```text
test_proj_sql_alchemy/
├── src/
│   ├── config.py       # Pydantic settings + SQLAlchemy URLs
│   ├── database.py     # Engines and session factories
│   ├── models.py       # ORM and Core table definitions
│   ├── orm.py          # CRUD, relationships, aggregations, windows
│   ├── core.py         # Core examples, including async variants
│   └── main.py         # Safe CLI with explicit commands
├── .env.example        # Template: no actual secrets
├── .gitignore
├── requirements.txt
├── README.md           # English documentation
└── README_RUS.md       # Original Russian learning notes
```

## Further work

- Add pytest tests with an isolated PostgreSQL database.
- Improve consistency between ORM and Core learning examples.
- Expand error handling and check exercises that assume specific row IDs.
- Add CI and optionally Docker Compose for a disposable local database.
- Add Alembic migrations when the schema becomes more stable.

**Author:** Marina Erokhina  
**Course reference:** SQLAlchemy video tutorial by Artem Shumeiko (Rutube).
