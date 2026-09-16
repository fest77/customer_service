"""
 这个模块消息处理模块
"""
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from atguigu.chitchat.chit_chat import ChitChat
from atguigu.clarify.clarify_response import ClarifyResponse
from atguigu.domain.message import UserMessage, ProcessResult, MessageType, BotMessage
from atguigu.domain.state import DialogueState, Turn, FocusedObject
from atguigu.knowledge.hanlder import KnowledgeHanlder
from atguigu.plan.models import TurnPlan, TurnPlanValidationResult, ClarifyReason
from atguigu.plan.turn_plan import TurnPlanner
from atguigu.plan.turn_plan_validation import TurnPlannValidator
from atguigu.task.command.models import SetSlotsCommand
from atguigu.task.flow.loader import FlowLoader
from atguigu.task.flow.models import FlowCatalog, Flow
from atguigu.task.flow.steps import FlowStep, CollectSlotStep
from atguigu.task.handler import TaskHandler


class DialogueEngine:
    def __init__(self,turn_planner:TurnPlanner,
                 turn_plann_validator:TurnPlannValidator,
                 task_handler:TaskHandler,
                 clarif_response:ClarifyResponse,
                 chit_chat:ChitChat,
                 knowledge_handler:KnowledgeHanlder):
        self.turn_planner = turn_planner
        self.turn_plann_validator = turn_plann_validator
        self.task_handler = task_handler
        self.clarif_response = clarif_response
        self.chit_chat = chit_chat
        self.knowledge_handler = knowledge_handler

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
            messages:list[BotMessage] \
                = await self._execute_object_message(user_message=user_message,state=state)

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
            return await self.clarif_response.responder(
                state=state,
                user_message=user_message,
                reason=validation_result.reason,
            )

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
            res = await self.knowledge_handler.handle(
                know_intents=turnPlan.knowledge.intents,
                state=state,
                user_message=user_message,
            )
            return res
        else:
            # 闲聊组件
            res = await self.chit_chat.handle(
                user_message=user_message,
                state=state,
            )
            return res

    # 3 处理对象类型消息
    async def _execute_object_message(self,state:DialogueState,
                                      user_message:UserMessage,)-> list[BotMessage]:
        # 1 把对象类型消息放到focused_object
        state.shared.focused_object = FocusedObject(
            **asdict(user_message.object)
        )

        # todo 抽取方法
        yaml_path = Path(__file__).parents[2] / 'flow_config' / 'user_flows.yml'
        flow_catalog: FlowCatalog = FlowLoader().load(yaml_path)

        # 2 判断是否可以填充槽位数据
        if self._can_fill_slots(state,flow_catalog):
            # 3 如果可以填充
            if user_message.object.type == 'order':
                slots = {'order_number':user_message.object.id}
            if user_message.object.type == 'product':
                slots = {'product_id':user_message.object.id}

            ## 构建command:SetSlotsCommand
            # {"command": "set_slots", "slots": {"<slot_name>": "<value>"}},
            command = SetSlotsCommand(
                command = 'set_slots',
                slots = slots
            )

            ## 调用TaskHandler的方法执行流程
            return await self.task_handler.handle(
                commands=[command],
                state=state,
                user_message=user_message,
                flows=flow_catalog
            )
        else:
            # 4 如果无法填充
            ## 执行澄清回复组件
            return await self.clarif_response.responder(
                state=state,
                user_message=user_message,
                reason=ClarifyReason.OBJECT_REQUIRES_INTENT
            )

    # 判断是否填充槽位数据
    def _can_fill_slots(self, state:DialogueState,flow_catalog:FlowCatalog)->bool:
        # 是否活跃任务
        active_task = state.tasks.active
        if not active_task:
            return False

        # 2 有活跃任务
        # 根据当前任务流程id，获取流程对象
        flow_id = active_task.flow_id
        flow: Flow = flow_catalog.get_flow_by_id(flow_id)

        # 从流程对象获取所有步骤列表，当前任务步骤id到列表找到步骤对应数据
        step: FlowStep = flow.get_step_by_id(active_task.step_id)

        # # 判断当前步骤是否collect类型
        if not isinstance(step, CollectSlotStep):
            return False

        if (step.slot_name == 'order_number') and (state.shared.focused_object.type == 'order'):
            return True

        if (step.slot_name == 'product_id') and (state.shared.focused_object.type == 'product'):
            return True

        return False

