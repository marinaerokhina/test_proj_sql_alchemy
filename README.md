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

## Run locally

Requires **Python 3.10+**, PostgreSQL, and a local database named `sqlalchemy_practice`. Copy `.env.example` to `.env` and set your database credentials.

From the project root:

```bash
pip install -r requirements.txt
python -m src.main init
python -m src.main seed
python -m src.main list
```

These commands create the tables, add sample workers, and display them. The basic workflow is tested with PostgreSQL in GitHub Actions. Other learning exercises in `src/orm.py` and `src/core.py` are examples, not a finished application.

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
