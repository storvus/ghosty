# import logging
# from typing import Protocol
#
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.aliases import UserId
# from src.models.message import Message
#
# logger = logging.getLogger(__name__)
#
#
# class MessageRepository(Protocol):
#
#     async def create_message(
#         self, from_user_id: UserId, to_user_id: UserId, message: str
#     ) -> Message: ...
#
#     async def get_message_history(
#         self, user_id: UserId, companion_id: UserId, limit: int = 50, offset: int = 0
#     ) -> list[Message]: ...
#
#
# class SqlAlchemyMessageRepository:
#     def __init__(self, db_session: AsyncSession):
#         self.db_session = db_session
#
#     async def create_message(
#         self, from_user_id: int, to_user_id: int, message: str
#     ) -> Message:
#         message = Message(
#             sender_id=from_user_id,
#             recipient_id=to_user_id,
#             content=message,
#         )
#         self.db_session.add(message)
#         return message
#
#     # ToDo: move pagination into service/constant
#     async def get_message_history(
#         self, user_id: UserId, companion_id: UserId, limit: int = 50, offset: int = 0
#     ) -> list[Message]:
#         query = (
#             select(Message)
#             .where(
#                 (Message.sender_id == user_id) & (Message.recipient_id == companion_id)
#                 | (Message.sender_id == companion_id)
#                 & (Message.recipient_id == user_id)
#             )
#             .order_by(Message.created_on.desc())
#             .limit(limit)
#             .offset(offset)
#         )
#         result = await self.db_session.execute(query)
#         return result.scalars().all()
