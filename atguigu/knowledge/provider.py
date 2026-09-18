"""
这个模块 创建provider，返回问题答案
"""
import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from atguigu.config.config import settings
from atguigu.domain.message import UserMessage, BotMessage
from atguigu.domain.state import DialogueState
from atguigu.utils import http_client


# 1 封装最终结果的类
@dataclass
class KnowledgeChunk:
    content: str = ""

# 创建provider基类，公共属性和抽象方法
class KnowledgeProvider(ABC):
    provider_id:str=""

    @abstractmethod
    async def provide(self,state:DialogueState,
                    user_message:UserMessage)->list[KnowledgeChunk]:
        pass

# 每个答案位置创建provider，继承基类，实现抽象方法
# api.product
class ProductProvider(KnowledgeProvider):
    provider_id = "api.product"
    # 实现抽象方法
    async def provide(self,
             state:DialogueState,user_message: UserMessage)->list[KnowledgeChunk]:
        # 获取商品id，从对象类型消息获取到
        focused_object = state.shared.focused_object
        if focused_object is None:
            return [KnowledgeChunk(content="请提供商品信息")]

        product_id = focused_object.id
        # 远程调用，调用中台系统接口
        url = f"{settings.commerce_api_base_url}/products/{product_id}"
        response = await http_client.http_client.get(url)
        data = response.json().get("data","没有信息")
        result = json.dumps(data,ensure_ascii=False)
        return [KnowledgeChunk(content=result)]

# api.order
# 约定需求：查询订单信息 要调用两个中台接口，一个查询订单详情信息 ，一个查询订单物流信息
# 调用两个接口，使用并行方式实现，不是串行，提高速度
class ApiOrderProvider(KnowledgeProvider):
    provider_id = "api.order"

    async def provide(self, state: DialogueState,
                      user_message: UserMessage) -> list[KnowledgeChunk]:
        # 从对象类型消息获取订单id
        focused_object = state.shared.focused_object
        if focused_object is None:
            return [KnowledgeChunk(content="请提供订单信息")]

        order_id = focused_object.id

        # 拼接调用接口地址
        url1 = f"{settings.commerce_api_base_url}/orders/{order_id}"
        url2 = f"{settings.commerce_api_base_url}/orders/{order_id}/logistics"

        # 并行方式
        # gather并行调用
        # 返回结果和gather传入顺序相关的
        order_info,logistics_info = await asyncio.gather(
            http_client.http_client.get(url1),
            http_client.http_client.get(url2),
        )

        result = json.dumps({
            "order_info":order_info.json().get('data','未知'),
            "logistics_info":logistics_info.json().get('data','未知'),
            },ensure_ascii=False
         )
        return [KnowledgeChunk(content=result)]

# faq.default
"""
    faq 代表常见问题
    设计： 
    1 在mysql创建数据库和表
    2 在表存储问题 和 对应答案
    3 根据用户输入问题 到 mysql表找到对应问题
      返回问题答案
"""
class FAQProvider(KnowledgeProvider):
    provider_id = 'faq.default'

    async def provide(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        # TODO
        return [KnowledgeChunk(content="未检索到相关问题")]

# rag.default
"""
    rag 一般用于查询商品操作步骤
    设计：
      之前智库项目
      远程调用，调用智库项目接口
"""
class RAGProvider(KnowledgeProvider):
    provider_id = 'rag.default'

    async def provide(self,
                       user_message: UserMessage,
                       state: DialogueState, ) -> list[KnowledgeChunk]:
        # RAG知识库查询知识接口（TODO）
        return [KnowledgeChunk(content="未检索到相关信息")]