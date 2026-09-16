"""
这个模块作用 定义知识检索范围
"""
from dataclasses import dataclass, field


# 1 封装知识检索数据
@dataclass
class KnowledgeIntent:
    id:str   # 范围值
    description:str  # 范围值对应中文描述
    # 当前范围问题 答案位置
    provider_ids:list[str]=field(default_factory=list)
    # 查询商品信息 product  订单信息  order 传入对应类型对象
    requires_object: str | None = None

# 创建字典
KNOWLEDGE_INTENTS: dict[str, KnowledgeIntent] = {
    "product_info": KnowledgeIntent(
        id="product_info", description="商品信息咨询",
        provider_ids=["api.product"], requires_object="product",
    ),
    "order_info": KnowledgeIntent(
        id="order_info", description="订单信息咨询",
        provider_ids=["api.order"], requires_object="order",
    ),

    "refund_policy": KnowledgeIntent(
        id="refund_policy", description="退款政策咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
    "return_policy": KnowledgeIntent(
        id="return_policy", description="退货政策咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
    "shipping_policy": KnowledgeIntent(
        id="shipping_policy", description="配送政策咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
    "platform_rule": KnowledgeIntent(
        id="platform_rule", description="平台规则咨询",
        provider_ids=["rag.default"],
    ),
    "general_ecommerce_info": KnowledgeIntent(
        id="general_ecommerce_info", description="电商通用信息咨询",
        provider_ids=["faq.default", "rag.default"],
    ),
}