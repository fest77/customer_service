from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.state import DialogueState

# 封装yaml的action属性值
@dataclass
class ActionCall:
    # 必须
    action_name: str

# 封装中台接口返回数据
@dataclass
class ActionResult:
    slot_updates: dict[str, Any] = field(default_factory=dict)

# 创建actioin基类
class Action(ABC):
    # name属性
    name = ""
    # 抽象方法，子类继承action基类，实现这个抽象方法
    @abstractmethod
    async def run(self,state:DialogueState)->ActionResult:
        pass
