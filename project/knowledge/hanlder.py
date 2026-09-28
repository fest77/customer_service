"""
这个模块作用 用于对外调用的
"""
from project.domain.message import UserMessage, BotMessage
from project.domain.state import DialogueState
from project.knowledge.intents import KNOWLEDGE_INTENTS
from project.knowledge.provider import KnowledgeProvider, KnowledgeChunk
from project.knowledge.registry import KnowledgeProviderRegistry
from project.knowledge.responder import KnowledgeResponseder


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
    async def handle(self,
                     know_intents: list[str],
                     state:DialogueState,
                     user_message:UserMessage,)->list[BotMessage]:
        # 1获取意图识别结果
        # list[str] ['product_info', 'refund_policy']
        # 2根据意图识别结果
        # 获取答案位置  provider_ids=["faq.default", "rag.default"]
        # provider_ids ，去重操作
        provider_ids:list[str] = self.get_provider_ids(know_intents)

        # 3 根据答案位置 provider_ids
        # 获取对应provider对象
        # 4 执行provider对象方法得到结果
        final_result:list[KnowledgeChunk] = []
        for provider_id in provider_ids:

            provider:KnowledgeProvider \
                = self.knowledge_registry.get_provider_by_id(provider_id)

            chunks:list[KnowledgeChunk] \
                = await provider.provide(state=state, user_message=user_message)

            final_result.extend(chunks)

        # 5 把provider对象方法结果提交LLM，对结果修改，返回用户
        bot_message:BotMessage = await self.know_responseder.responsed(
            chunks=final_result,
            state=state,
            user_message=user_message
        )
        return [bot_message]

    # 获取答案位置  根据 ['product_info', 'refund_policy']
    # provider_ids ，去重操作
    def get_provider_ids(self, know_intents:list[str]) -> list[str]:
        final_result:list[str] = []
        for intent in know_intents:
            final_result.extend(KNOWLEDGE_INTENTS[intent].provider_ids)
        # 去重方式1：缺陷：  set无序
        return list(set(final_result))

        # 去重方式2 保证顺序
        # list(dict.fromkeys(final_result))

