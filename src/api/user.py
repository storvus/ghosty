from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.dependencies import get_user_service, get_current_user
from src.dto.current_user import CurrentUser
from src.dto.login_request import LoginRequest
from src.dto.register_request import RegisterRequest
from src.dto.search_request import SearchRequest
from src.dto.token_response import TokenResponse
from src.dto.user_response import UserResponse
from src.services.user import UserService

router = APIRouter(tags=["User"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
)
async def register(body: RegisterRequest, user_service: Annotated[UserService, Depends(get_user_service)]):
    return await user_service.register(body)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(body: LoginRequest, user_service: Annotated[UserService, Depends(get_user_service)]):
    return await user_service.login(body)


@router.post(
    "/search",
    response_model=list[UserResponse],  # ToDo: to bring to the page format
)
async def search(
    body: SearchRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    return await user_service.search(body, current_user)


