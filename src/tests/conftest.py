import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings
from src.core.db import Base


@pytest_asyncio.fixture()
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
def migrate_db():
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")


# @pytest_asyncio.fixture(autouse=True)
# async def truncate_tables(db_engine, request):
#     # Skip DB operations for unit tests marked with 'no_db'
#     if request.node.get_closest_marker("no_db"):
#         yield
#         return
#
#     table_names = ", ".join(t.name for t in Base.metadata.sorted_tables)
#     async with db_engine.connect() as conn:
#         async with conn.begin():
#             await conn.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
#     yield
