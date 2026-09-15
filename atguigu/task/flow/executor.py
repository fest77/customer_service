"""
这个模块作用
 用于推进流程的步骤
"""
from atguigu.domain.message import BotMessage, UserMessage
from atguigu.domain.state import DialogueState
from atguigu.plan.models import TaskTurnPlan
from atguigu.task.action.base import ActionCall, ActionResult
from atguigu.task.action.runner import ActionRunner
from atguigu.task.flow.links import FlowStepLink, ConditionalLink, FallbackLink
from atguigu.task.flow.models import FlowCatalog, Flow
from atguigu.task.flow.steps import FlowStep, StartFlowStep, ResponseFlowStep, CollectSlotStep, ActionFlowStep, \
    EndFlowStep
from atguigu.task.response.renderer import ResponseTemplateRender


class FlowExecutor:
    def __init__(self, response_render:ResponseTemplateRender,
                 action_runner:ActionRunner):
        self.response_render = response_render
        self.action_runner = action_runner

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
                # 推进到下一步
                self._run_next_step(step,state)
                continue

            """
                ResponseFlowStep
                * 渲染数据，组装返回数据
                * 这个步骤经常在action步骤后面，用于把action返回数据渲染
                * jinja2技术 
            """
            if isinstance(step, ResponseFlowStep):
                # 数据渲染
                bot_mesasge:BotMessage = (
                    self.response_render.render_response(
                        step.template,
                        state
                    ))
                # 放到当前bot_messages列表
                bot_messages.append(bot_mesasge)
                # 推进下一步
                self._run_next_step(step,state)
                continue

            """
                CollectSlotStep
                * 收集槽位数据
                * 从当前获取任务获取槽位数据
                * 从聚焦对象里面获取槽位数据
            """
            if isinstance(step, CollectSlotStep):
                # 调用方法，返回bool， 约定需要用户输入 true，不需要用户输入fasle
                # # 我的订单号1001，我想查物流状态： 不需要用户输入fasle，推进到下一步
                # # 我想查物流状态：    需要用户输入 true
                need_input:bool = self._run_collect_step(step,state,bot_messages)
                # 判断
                if need_input: # 我想查物流状态：    没有槽位数据，需要用户输入 true
                    return bot_messages

                else: # 我的订单号1001，我想查物流状态： 有槽位数据，不需要用户输入fasle，
                    # 推进到下一步
                    self._run_next_step(step,state)
                    continue

            """
                ActionFlowStep
                * 执行具体业务方法，调用中台系统接口实现具体功能
            """
            if isinstance(step, ActionFlowStep):
                #1 获取action步骤里面action属性值
                # action: action_lookup_order_status
                action_name = step.action
                action_call = ActionCall(
                    action_name=action_name,
                )

                #2 调用ActionRunner方法实现
                action_result:ActionResult = await self.action_runner.run(
                    state=state,
                    action_call=action_call
                )

                #3 把远程调用返回结果放到槽位里面
                # 为了后面从槽位获取数据渲染
                state.tasks.active.slots.update(action_result.slot_updates)

                #4 推进到下一步
                self._run_next_step(step,state)
                continue

            """
                EndFlowStep
                * 当前流程结束
            """
            if isinstance(step, EndFlowStep):
                state.tasks.active = None
                return bot_messages


    # 1 推进到下一步
    def _run_next_step(self, step, state):
        # 获取当前步骤的next属性值
        next_setp_id = self._get_next_step(state,step.next)
        # 把获取next属性值变成当前步骤id
        state.tasks.active.step_id = next_setp_id

    # 获取当前步骤next属性值
    def _get_next_step(self,
                state:DialogueState,
                next:list[FlowStepLink])->str:
        # 如果next字符串，无条件跳转
        if len(next)==1:
            return next[0].target

        # 如果next列表形式， if then else，有条件跳转
        # next列表遍历
        for link in next:
            if isinstance(link, ConditionalLink):
                # 判断if 里面表达式是否成立
                result = bool(eval(link.condition,{},
                             {"slots":state.tasks.active.slots}))
                if result:
                    return link.target
                continue
            if isinstance(link, FallbackLink):
                return link.target

    # 2 判断是否有槽位数据
    def _run_collect_step(self,
                   step:CollectSlotStep,
                   state:DialogueState,
                   bot_messages:list[BotMessage])->bool:
        # 1 从当前活跃任务 查询是否有槽位数据
        slots:dict = state.tasks.active.slots
        slot_value = slots.get(step.slot_name)

        # 2 如果活跃任务没有槽位数据，到focused_object
        # 如果找到了，再放到active里面
        if not slot_value:
            self.get_focused_object_slot_value(step,state)

        # 3 在上面两个地方找槽位数据，如果都没有找到，等待用户输入
        slot_value = state.tasks.active.slots.get(step.slot_name)
        if not slot_value:
            # 把等待用户输入提示信息，渲染
            bot_message:BotMessage = (
                self.response_render.render_response(step.template,state))
            bot_messages.append(bot_message)
            return True
        else:
            return False

    # 2 到focused_object槽位数据
    # 如果找到了，再放到active里面
    def get_focused_object_slot_value(self, step, state):
        # focused_object是否为空
        if not state.shared.focused_object:
            return
        # 如果focused_object不为空
        if (step.slot_name == 'order_number'
                and state.shared.focused_object.type=='order'):
            state.tasks.active.slots.update({step.slot_name:state.shared.focused_object.id})
            return
        if (step.slot_name == 'product_id'
                and state.shared.focused_object.type=='product'):
            state.tasks.active.slots.update({step.slot_name:state.shared.focused_object.id})
            return


# eval方法
if __name__ == "__main__":
    data = {
        "slots":{
            "product":"abcd",
            "product": "abcd",
            "product": "abcd"
        }
    }
    res = bool(eval("slots.get('product_id')",{},data))
    print(res)
