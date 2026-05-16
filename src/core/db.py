from sqlalchemy.orm import DeclarativeBase

# from server.core.config import settings


class Base(DeclarativeBase):
    pass


engine = None
async_session = None


# def get_engine():
#     global engine
#     if engine is None:
#         engine = create_async_engine(settings.DATABASE_URL)
#     return engine
#
#
# def get_async_sessionmaker():
#     global async_session
#     if async_session is None:
#         async_session = async_sessionmaker(get_engine(), expire_on_commit=False)
#     return async_session
#
#
# async def get_session():
#     session_factory = get_async_sessionmaker()
#     async with session_factory() as session:
#         yield session
