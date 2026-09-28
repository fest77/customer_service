"""
这个模块负责实现任务流程调用过程
任务流程有三个组件实现
调用三个组件
**-- CommandProcessor： 根据意图识别结果更新state数据**
**-- TaskLifecycleResponder：**根据不同任务状态变化生成不同中文提示信息
**-- FlowExecutor：推进流程里面步骤*
"""
from project.domain.message import BotMessage, UserMessage
from project.domain.state import DialogueState
from project.task.command.models import Command
from project.task.command.processor import CommandProcessor
from project.task.flow.executor import FlowExecutor
from project.task.flow.models import FlowCatalog
from project.task.lifecycle.models import TaskEvent
from project.task.lifecycle.responder import TaskLifecycleResponder


class TaskHandler:
    # 注入
    def __init__(self,command_processor:CommandProcessor,
                 task_lifecycle:TaskLifecycleResponder,
                 flow_executor: FlowExecutor):
        self.command_processor = command_processor
        self.task_lifecycle = task_lifecycle
        self.flow_executor = flow_executor

    # 调用的方法
    # commands: 意图识别结果列表
    # flows:所有流程数据
    async def handle(self,commands: list[Command],
            state: DialogueState,
            flows: FlowCatalog,
            user_message:UserMessage)->list[BotMessage]:
        # 1 根据意图识别结果，调用CommandProcessor更新state状态数据
        events:list[TaskEvent] = await self.command_processor.run(
            commands=commands,
            state=state,
            flows=flows,
        )

        # 2 根据CommandProcessor返回结果,调TaskLifecycleResponder生成不同中文提示
        messages:list[BotMessage] = await self.task_lifecycle.responder(
            events=events,
            flow_catalog=flows,
        )

        # 3 调用FlowEXecutor推进步骤实现
        bot_messages:list[BotMessage] = await self.flow_executor.run_step(
            state=state,
            flows=flows,
        )
        messages.extend(bot_messages)
        return messages
