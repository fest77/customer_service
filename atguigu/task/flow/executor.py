"""
这个模块作用
 用于推进流程的步骤
"""
from atguigu.domain.message import BotMessage, UserMessage
from atguigu.domain.state import DialogueState
from atguigu.plan.models import TaskTurnPlan
from atguigu.task.flow.models import FlowCatalog, Flow
from atguigu.task.flow.steps import FlowStep, StartFlowStep, ResponseFlowStep, CollectSlotStep, ActionFlowStep, \
    EndFlowStep

class FlowExecutor:
    async def run_step(self,
           state: DialogueState,
        flows: FlowCatalog,
         user_message:UserMessage) -> list[BotMessage]:
        bot_messages:list[BotMessage] = []
        # 判断是否存在活跃任务
        if not state.tasks.active:
            return bot_messages

        # 有活跃任务
        # while True:
        # 约定最多100循环
        for _ in range(100):
            # 从当前活跃任务获取步骤数据
            flow:Flow = flows.get_flow_by_id(state.tasks.active.flow_id)
            step:FlowStep = flow.get_step_by_id(state.tasks.active.step_id)

            # 判断不同类型步骤
            # 五种
            """
             StartFlowStep
             * 推进到下一步
             ** next属性： 
             *** 无条件跳转
             *** 有条件跳转   eval()
            """
            if isinstance(step, StartFlowStep):
                pass

            """
                ResponseFlowStep
                * 渲染数据，组装返回数据
                * 这个步骤经常在action步骤后面，用于把action返回数据渲染
                * jinja2技术 
            """
            if isinstance(step, ResponseFlowStep):
                pass

            """
                CollectSlotStep
                * 收集槽位数据
                * 从当前获取任务获取槽位数据
                * 从聚焦对象里面获取槽位数据
            """
            if isinstance(step, CollectSlotStep):
                pass

            """
                ActionFlowStep
                * 执行具体业务方法，调用中台系统接口实现具体功能
            """
            if isinstance(step, ActionFlowStep):
                pass

            """
                EndFlowStep
                * 当前流程结束
            """
            if isinstance(step, EndFlowStep):
                state.tasks.active = None
                return bot_messages
