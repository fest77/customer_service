from pydantic import BaseModel

class ChatObject(BaseModel):
    type: str
    id: str
    title: str | None = None
    attributes: dict = {}

class ChatMessage(BaseModel):
    text: str | None = None
    object: ChatObject | None = None

# {sender_id: "u1001", text: "我想退单"}
# 封装前端传递过来数据
class ChatRequest(BaseModel):
    sender_id: str # 用户id
    text: str | None = None # 文本消息

    # 用户发送消息有两种类型：
    ## 第一种 文本类型
    ## 第二种 对象类型
    # 对象类型消息，比如发送订单
    object: ChatObject | None = None
    message_id: str | None = None # 消息唯一标识，需要自己生成 使用uuid

# 封装响应数据
class ChatResponse(BaseModel):
    sender_id: str
    message_id: str
    messages: list[ChatMessage]

###########################
class HistoryMessage(BaseModel):
    role: str # user/bot
    text: str | None = None
    object: ChatObject | None = None


class HistoryResponse(BaseModel):
    sender_id: str
    messages: list[HistoryMessage]