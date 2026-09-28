import uuid
from dataclasses import asdict

from fastapi import APIRouter
from fastapi.params import Depends

from project.api.depends import get_dialogue_service
from project.api.schemas import ChatRequest, ChatResponse, ChatMessage, ChatObject, HistoryResponse, HistoryMessage
from project.domain.message import UserMessage, ProcessResult, MessageType, MessageObject
from project.domain.state import DialogueState
from project.service.dialogue_service import DialogueService

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

# 根据用户id查询历史记录接口
@chat_router.get("/api/chat/history")
async def chat(sender_id:str,
        service:DialogueService=Depends(get_dialogue_service))->HistoryResponse:
    # 根据用户id，调用service方法实现
    state:DialogueState = await service.get_history_info(sender_id)
    # 把查询历史记录封装HistoryResponse
    messages:list[HistoryMessage] = []

    # 获取历史记录用户问题 和对应回答
    # 遍历所有session，得到每个session会话
    for session in state.shared.sessions:
        # 从每个session获取turns
        # turns遍历得到每个turn
        for turn in session.turns:
            # 用户提问
            messages.append(HistoryMessage(
                role="user",
                text=turn.user_message.text,
                object=ChatObject(
                    **asdict(turn.user_message.object)
                ) if turn.user_message.object else None,
            ))

            # 客服回复
            messages.extend(
                [
                    HistoryMessage(
                        role="bot",
                        text=message.text,
                        object=None
                    )
                    for message in turn.bot_message
                ]
            )

    return HistoryResponse(
        sender_id=sender_id,
        messages=messages
    )
