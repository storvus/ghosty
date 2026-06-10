# from typing import Annotated
#
# from fastapi import APIRouter, Depends
#
# from src.aliases import UserId
# from src.api.dependencies import get_message_repo, get_user_repo
# from src.repositories.message import MessageRepository
# from src.repositories.user import UserRepository
#
# router = APIRouter(tags=["User"])
#
#
# @router.get("/history")
# async def get_history(
#         username: str,
#     companion_id: UserId,
#     user_repo: Annotated[UserRepository, Depends(get_user_repo)],
#     message_repo: Annotated[MessageRepository, Depends(get_message_repo)],
# ):
#     user_id = await user_repo.get_user_id_by_username(username)
#     messages = await message_repo.get_message_history(user_id, companion_id)
#     return {
#         "total": 0,
#         # ToDo: introduce a serializer?
#         "results": [
#             {
#                 "from_user_id": message.sender_id,
#                 "to_user_id": message.recipient_id,
#                 "message": message.content,
#                 "created_on": message.created_on.isoformat(),
#             }
#             for message in messages
#         ],
#     }
