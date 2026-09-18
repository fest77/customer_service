from contextlib import asynccontextmanager

from fastapi import FastAPI

from atguigu.api.chat_router import chat_router
from atguigu.utils.database import init_db_engine, close_engine
from atguigu.utils.http_client import init_http_client, close_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_http_client()
    init_db_engine()
    yield
    await close_engine()
    await close_http_client()

app = FastAPI(lifespan=lifespan)
# fastapi对象
# app = FastAPI()

app.include_router(chat_router)