"""
这个模块作用 用于对外调用的
"""
from atguigu.knowledge.registry import KnowledgeProviderRegistry
from atguigu.knowledge.responder import KnowledgeResponseder


class KnowledgeHanlder:
    def __init__(self,
                 knowledge_registry: KnowledgeProviderRegistry,
                 know_responseder: KnowledgeResponseder):
        self.knowledge_registry = knowledge_registry
        self.know_responseder = know_responseder

    """
        1 获取意图识别结果 list[str]  ['product_info' ,'refund_policy']
        2 根据意图识别结果 获取答案位置 provider_ids ，去重操作
        3 根据答案位置 provider_ids 获取对应provider对象
        4 执行provider对象方法得到结果
        5 把provider对象方法结果提交LLM，对结果修改，返回用户
    """
    async def handle(self):
        pass
