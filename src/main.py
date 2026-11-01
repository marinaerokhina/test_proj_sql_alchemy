"""Command-line entry point for safe, explicit learning exercises."""
import argparse

from src.orm import SyncORM


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SQLAlchemy practice with a local PostgreSQL database."
    )
    parser.add_argument(
        "command", choices=["init", "seed", "list"],
        help="init: create tables; seed: add sample workers; list: print workers",
    )
    args = parser.parse_args()

    if args.command == "init":
        SyncORM.create_tables()
        print("Schema initialized (existing tables preserved).")
    elif args.command == "seed":
        SyncORM.insert_data()
        print("Sample workers inserted.")
    elif args.command == "list":
        SyncORM.select_workers()


if __name__ == "__main__":
    main()
