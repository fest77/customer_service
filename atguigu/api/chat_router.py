import uuid

from fastapi import APIRouter

from atguigu.api.schemas import ChatRequest, ChatResponse, ChatMessage

chat_router = APIRouter()

# todo
@chat_router.post("/api/chat")
async def chat(chatRequest:ChatRequest)->ChatResponse:
    # 1 获取前端传入数据，封装到ChatRequest
    # 2 把api层ChatRequest对象 转换 service层数据模型对象
    # 3 注入service对象，调用service方法
    # 4 获取service方法返回结果，把service返回类型转换api层ChatResponse
    # 5 返回转换之后api层ChatResponse对象
    return ChatResponse(
        sender_id=chatRequest.sender_id,
        message_id=str(uuid.uuid4()),
        messages=[
            ChatMessage(
                text="hello",
                object=None
            )
        ]
    )