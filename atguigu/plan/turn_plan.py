"""
这个模块用户问题意图识别
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.message import UserMessage
from atguigu.domain.state import DialogueState
from atguigu.plan.models import TurnPlan
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.task.flow.models import FlowCatalog
from atguigu.utils.llm_client import llm


# RAFT
## Role：明确告诉LLM当前身份角色是什么
## Action：明确告诉LLM当前做事情是什么
## Format：明确告诉LLM以什么格式输出，输出示例
## Tone：语气，以专家口吻...
class TurnPlanner:
    async def plan(self,
                   user_message:UserMessage,
                   state:DialogueState,
                   flow_catalog:FlowCatalog):
        # 加载提示词模版
        prompt_text = load_prompt('turn_plan')
        prompt = PromptTemplate.from_template(
            prompt_text,template_format='jinja2'
        )

        # 创建调用链
        chain = prompt | llm | JsonOutputParser()

        # todo 获取提示词需要数据
        # 执行invoke，得到结果
        res = chain.ainvoke({
            "user_message": HistoryBuilder.render_user_message(user_message),
            "flows_json": flow_catalog,
            "knowledge_intents_json":{},
            "task_state_json":state,
            "focused_object_json":{},
            "conversation_history":state
        })

        # LLM返回json转换TurnPlan
        return TurnPlan.from_dict(res)