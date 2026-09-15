"""
这个模块
对外调用
在FlowExecutor的action类型步骤调用这个模块方法实现
"""
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import ActionCall, Action, ActionResult
from atguigu.task.action.registry import ActionRegistry


class ActionRunner:
    def __init__(self,registry:ActionRegistry):
        self._registry = registry

    # 对外提供的方法
    # 在FlowExecutor的action类型步骤调用的方法
    # 参数 action_call：action步骤里面action属性值
    async def run(self,action_call:ActionCall,
                      state:DialogueState)->ActionResult:
        # 1 根据yaml中 action步骤里面action属性值 找到对应action对象
        action_name = action_call.action_name
        action:Action = self._registry.get_action(action_name)

        # 2 找到action对象之后，执行方法远程调用
        # 3 远程调用之后，返回结果
        return await action.run(state)