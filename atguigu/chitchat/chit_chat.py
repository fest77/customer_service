"""
这个模块用户执行闲聊轨道
和LLM聊天
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.message import UserMessage, BotMessage
from atguigu.domain.state import DialogueState
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.utils.llm_client import llm


class ChitChat:
    async def handle(self,
                user_message:UserMessage,
                state:DialogueState)->list[BotMessage]:
        prompt_text = load_prompt("chitchat_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,template_format="jinja2")

        chain = prompt | llm | StrOutputParser()

        response = await chain.ainvoke({
            "history": HistoryBuilder.build(state.shared.sessions[-1].turns),
            "user_message": HistoryBuilder.render_user_message(user_message),
        })
        return [BotMessage(text=response)]