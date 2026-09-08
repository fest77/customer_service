from fastapi import FastAPI

from atguigu.api.chat_router import chat_router

# fastapi对象
app = FastAPI()

app.include_router(chat_router)