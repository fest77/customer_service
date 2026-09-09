import uuid
from dataclasses import asdict

from fastapi import APIRouter
from fastapi.params import Depends

from atguigu.api.depends import get_dialogue_service
from atguigu.api.schemas import ChatRequest, ChatResponse, ChatMessage, ChatObject
from atguigu.domain.message import UserMessage, ProcessResult, MessageType, MessageObject
from atguigu.service.dialogue_service import DialogueService

chat_router = APIRouter()

@chat_router.post("/api/chat")
async def chat(chatRequest:ChatRequest,
               service:DialogueService=Depends(get_dialogue_service))->ChatResponse:
    # 1 获取前端传入数据，封装到ChatRequest
    # 2 把api层ChatRequest对象 转换 service层数据模型对象UserMessage
    #  ChatRequest ==> UserMessage
    user_message:UserMessage = _build_user_message(chatRequest)

    # 3 注入service对象，调用service方法
    process_result:ProcessResult= await service.process_message(user_message)

    # 4 获取service方法返回结果 ProcessResult，把service返回类型转换api层ChatResponse
    # ProcessResult -- ChatResponse
    chat_response:ChatResponse= _build_chat_response(process_result)

    # 5 返回转换之后api层ChatResponse对象
    return chat_response

# 2 把api层ChatRequest对象 转换 service层数据模型对象UserMessage
    #  ChatRequest ==> UserMessage
def _build_user_message(chatRequest:ChatRequest)->UserMessage:
    return UserMessage(
        sender_id=chatRequest.sender_id,
        message_id=chatRequest.message_id
               if chatRequest.message_id else str(uuid.uuid4()),
        type=MessageType.TEXT
             if chatRequest.text else MessageType.OBJECT,
        text=chatRequest.text,
        # ChatObject ==> MessageObject
        object=MessageObject(
            id = chatRequest.object.id,
            type = chatRequest.object.type,
            title = chatRequest.object.title,
            attributes = chatRequest.object.attributes,
        ) if chatRequest.object else None,
    )

# 4 获取service方法返回结果 ProcessResult，把service返回类型转换api层ChatResponse
    # ProcessResult -- ChatResponse
def _build_chat_response(process_result:ProcessResult)->ChatResponse:
    return ChatResponse(
        sender_id=process_result.sender_id,
        message_id=process_result.message_id,
        # process_result里面messages列表遍历得到每个BotMessage对象
        # 把每个BotMessage对象转换 ChatMessage
        messages=[
            ChatMessage(
                text=bot_message.text,
                object=ChatObject(
                    **asdict(bot_message.object)
                ) if bot_message.object else None,
            )
            for bot_message in process_result.messages
        ]
    )