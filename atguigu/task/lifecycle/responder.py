"""
这个模块是TaskHandler的一个组件
作用：根据返回TaskEvent对象，返回不同中文提示
"""
from atguigu.domain.message import BotMessage
from atguigu.task.flow.models import FlowCatalog
from atguigu.task.lifecycle.models import TaskEvent, TaskStarted, TaskSwitched, TaskResumed, TaskCanceled


class TaskLifecycleResponder:
    async def responder(self,events:list[TaskEvent],
                        flow_catalog:FlowCatalog)->list[BotMessage]:
        messages:list[BotMessage]=[]
        for event in events:
            bot_message:BotMessage =self.execute_taskevent(event,flow_catalog)
            messages.append(bot_message)
        return messages

    def execute_taskevent(self, event:TaskEvent,flow_catalog:FlowCatalog)->BotMessage:
        if isinstance(event,TaskStarted):
            # 获取event里面flow_id  根据flow_id获取流程名称
            flow = flow_catalog.get_flow_by_id(event.task.flow_id)
            return BotMessage(text=f"好的，现在开始处理{flow.name}")

        if isinstance(event,TaskSwitched):
            previous_flow = flow_catalog.get_flow_by_id(event.previous.flow_id)
            current_flow = flow_catalog.get_flow_by_id(event.current.flow_id)
            return BotMessage(text=f"好的，先把{previous_flow.name}暂停"
                                   f" 现在要开始{current_flow.name}")

        if isinstance(event,TaskResumed):
            flow = flow_catalog.get_flow_by_id(event.task.flow_id)
            return BotMessage(text=f"好的，继续刚才{flow.name}")

        if isinstance(event,TaskCanceled):
            flow = flow_catalog.get_flow_by_id(event.task.flow_id)
            return BotMessage(text=f"好的，取消{flow.name}")

