import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import chat, user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_V1_PREFIX = "/api"

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# app.include_router(gateway.router)
app.include_router(user.router, prefix=API_V1_PREFIX)
app.include_router(chat.router, prefix=API_V1_PREFIX)
