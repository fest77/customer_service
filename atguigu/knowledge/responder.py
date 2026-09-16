"""
这个模块作用 把provider返回结果构建提示词，提交LLM
有LLM修改结果返回用户
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.message import UserMessage, BotMessage
from atguigu.domain.state import DialogueState
from atguigu.knowledge.provider import KnowledgeChunk
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.utils.llm_client import llm


class KnowledgeResponseder:
    # chunks:list[KnowledgeChunk] 是provider执行返回结果
    async def responsed(self,
                        chunks:list[KnowledgeChunk],
                        state:DialogueState,
                        user_message:UserMessage
                        )->BotMessage:
        # 加载提示词模版
        prompt_text = load_prompt("knowledge_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2")

        # 创建调用链
        chain = prompt | llm | StrOutputParser()

        # 调用
        res = await chain.ainvoke(
            {
                "knowledge_content": "\n".join(
                    [chunk.content
                    for chunk in chunks]
                ),
                "history": HistoryBuilder.build(state.shared.sessions[-1].turns),
                "user_message":HistoryBuilder.render_user_message(user_message)
            }
        )
        return BotMessage(text=res)