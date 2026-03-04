# from src.core import create_tables, insert_data
# import asyncio

from src.orm import SyncORM, AsyncORM
from src.core import SyncCore, AsyncCore

SyncORM.create_tables()
SyncORM.insert_data()
SyncORM.select_workers()
SyncORM.update_workers()
#asyncio.run(insert_data())
#SyncCore.create_tables()
#SyncCore.insert_data()
#SyncCore.select_workers()
#SyncCore.update_workers()