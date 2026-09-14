"""
 这个模块消息处理模块
"""
import time
import uuid
from pathlib import Path

from atguigu.domain.message import UserMessage, ProcessResult, MessageType, BotMessage
from atguigu.domain.state import DialogueState, Turn
from atguigu.plan.models import TurnPlan, TurnPlanValidationResult
from atguigu.plan.turn_plan import TurnPlanner
from atguigu.plan.turn_plan_validation import TurnPlannValidator
from atguigu.task.flow.loader import FlowLoader
from atguigu.task.flow.models import FlowCatalog
from atguigu.task.handler import TaskHandler


class DialogueEngine:

    def __init__(self,turn_planner:TurnPlanner,
                 turn_plann_validator:TurnPlannValidator,
                 task_handler:TaskHandler):
        self.turn_planner = turn_planner
        self.turn_plann_validator = turn_plann_validator
        self.task_handler = task_handler

    async def process_message(self,
                state:DialogueState,
                user_message:UserMessage) -> ProcessResult:
        # 1 准备当前session
        self._prepare_current_session(state)

        # 2 判断消息类型
        ## 2.1 文件类型消息
        if user_message.type == MessageType.TEXT:
            messages:list[BotMessage] = await self._execute_text_message(
                user_message=user_message,state=state)
        else:
            ## 2.2 对象类型消息
            messages:list[BotMessage] = await self._execute_object_message()

        # 3 提交state最新消息数据
        # 一轮对话：一问一答 或者 一问多答
        turn = Turn(
            turn_id=str(uuid.uuid4()),
            user_message=user_message,
        )
        turn.bot_message.extend(messages)

        # list操作
        # append 追加 ['1','2'].append ['3'] ==> ['1','2',['3']]
        # extend 合并['1','2'].extend ['3'] ==> ['1','2','3']

        # dict  update方法  合并
        # {a:1,b:2} .update {c:3} ==> {a:1,b:2,c:3}
        state.shared.sessions[-1].turns.append(turn)

        # 4 返回处理结果
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=messages,
        )

    # 1 准备当前session
    def _prepare_current_session(self,state:DialogueState):
        # 判断当前是否有session
        # 如果当前没有session，创建新session
        if not state.shared.sessions:
            state.shared.create_session()
        # 如果当前有session，判断session是否过期
        else:
            ## 过期：60分钟不活跃过期
            ## 如果过期，创建新session
            # 获取当前session
            current_session = state.shared.sessions[-1]
            ## 当前时间  从1970-01-01   秒
            now = time.time()
            if now - current_session.last_activity_at > 60*60:
                state.shared.create_session()
            else: # 没有过期
                # 最后一次活跃时间变成当前时间
                current_session.last_activity_at = now

    # 2 处理文本消息
    async def _execute_text_message(self,user_message:UserMessage,
                    state:DialogueState) -> list[BotMessage]:
        yaml_path = Path(__file__).parents[2]/'flow_config'/'user_flows.yml'
        flow_catalog:FlowCatalog = FlowLoader().load(yaml_path)
        # 1 根据用户输入问题，调用TurnPlanner方法进行意图识别，返回意图识别结果
        # 调用LLM，使用参数数据构建提示词
        # 参数：用户问题   历史数据   流程数据   知识检索数据
        turnPlan:TurnPlan= await self.turn_planner.plan(
                    user_message,state,flow_catalog)

        # 2 根据意图识别结果，调用TurnPlannValidator方法进行校验
        validation_result:TurnPlanValidationResult = (
            self.turn_plann_validator.validation(turnPlan,state,flow_catalog))

        # 3 校验没有通过，执行反问澄清组件
        if not validation_result.valid:
            # 反问澄清组件
            pass

        # 3 校验通过，根据意图识别结果执行不同轨道
        if turnPlan.task:
            # 调用任务流程组件推进步骤实现
            result = await self.task_handler.handle(
                commands=turnPlan.task.commands,
                state=state,
                flows=flow_catalog,
                user_message=user_message,
            )
            return result

        if turnPlan.knowledge:
            # 知识检索组件
            pass
        else:
            # 闲聊组件
            pass

    # 3 处理对象类型消息
    async def _execute_object_message(self):
        pass


