"""
这个模块用户问题意图识别
"""
import json
from dataclasses import asdict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.message import UserMessage
from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.plan.models import TurnPlan
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.task.flow.models import FlowCatalog, Flow
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

        # 获取提示词需要数据
        # 用户消息
        user_message = HistoryBuilder.render_user_message(user_message)
        # 最近一次session里面多轮记录
        turns = state.shared.sessions[-1].turns
        conversation_history = HistoryBuilder.build(turns)
        # 对象类型消息
        focused_object_json = json.dumps(asdict(state.shared.focused_object)
                                 if state.shared.focused_object else None)
        # 任务流程特有数据
        task_state_json = json.dumps(asdict(state.tasks)
                                     if state.tasks else None)
        # flows_json yaml文件流程数据
        ## 把yaml文件流程数据flow_catalog，不包含步骤数据
        flows:dict[str, Flow] = flow_catalog.flows
        # flows字典遍历，得到每个Flow，去掉每个Flow里面steps
        flows_json = [
            {
              k:v  for k,v in asdict(flow).items()
                if k != 'steps'
            }
            for flow in flows.values()
        ]
        # 知识检索范围数据
        knowledge_intents_json = json.dumps(
            [
                {
                    "id":intent.id,
                    "description":intent.description
                }
                for intent in KNOWLEDGE_INTENTS.values()
            ]
        )

        # 执行invoke，得到结果
        res = await chain.ainvoke({
            "user_message": user_message,
            "flows_json": flows_json,
            "knowledge_intents_json":knowledge_intents_json,
            "task_state_json":task_state_json,
            "focused_object_json":focused_object_json,
            # 幻觉 ： 1 提示词边界约定不严谨
            #        2 构建提示词数据有很多干扰数据
            #        3 模型本身能力很弱
            "conversation_history":conversation_history
        })

        # LLM返回json转换TurnPlan
        return TurnPlan.from_dict(res)