from fastapi import FastAPI

from atguigu.api.chat_router import chat_router

# fastapi对象
app = FastAPI()

# 把 chat_router 中定义的路由，注册到 app 上
app.include_router(chat_router)