"""
这个模块 注册action对象
 创建字典：key是action的name属性值  value是action对象
"""
from typing import Any

from atguigu.task.action.base import Action


class ActionRegistry:
    # 初始化字典
    def __init__(self):
        self._actions:dict[str,Action] = {}

    # 注册action方法，想字典放action对象
    def register_action(self, action:Action):
        self._actions[action.name] = action

    # 从字典获取action对象的方法
    # 传递参数 action名称 （yaml文件action属性名称）
    def get_action(self,name:str)->Action:
        return self._actions.get(name)


