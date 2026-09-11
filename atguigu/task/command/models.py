# | command       | 完整形式
# | 作用                      |
# | ------------- | ------------------------------------------------------------ | ------------------------- |
# | `start_flow`  | `{"command": "start_flow", "flow": "<flow_id>"}`             | 启动指定 Flow。           |
# | `set_slots`   | `{"command": "set_slots", "slots": {"<slot_name>": "<value>"}}` | 向当前活动任务写入 Slot。 |
# | `cancel_task` | `{"command": "cancel_task", "task_id": "<task_id>"}`         | 取消指定任务。            |
# | `resume_task` | `{"command": "resume_task", "task_id": "<task_id>"}`         | 恢复指定的暂停任务。      |
from dataclasses import dataclass
from typing import Any

# 数据模型，封装意图识别组件返回数据
@dataclass
class Command:
    command: str
    # 把dict转换不同任务对应的对象
    # 前向引用
    # `{"command": "start_flow", "flow": "<flow_id>"}`
    @classmethod
    def from_dict(cls,command_data: dict) -> "Command":
        # clz  StartFlowCommand
        clz = COMMAND_NAME_TO_CLASS[command_data["command"]]
        return clz(**command_data)


# start_flow
@dataclass
class StartFlowCommand(Command):
    flow: str

# set_slots
@dataclass
class SetSlotsCommand(Command):
    slots: dict[str, Any]

# cancel_task
@dataclass
class CancelTaskCommand(Command):
    task_id: str

# resume_task
@dataclass
class ResumeTaskCommand(Command):
    task_id: str


COMMAND_NAME_TO_CLASS: dict[str, type[Command]] = {
    "start_flow": StartFlowCommand,
    "set_slots": SetSlotsCommand,
    "cancel_task": CancelTaskCommand,
    "resume_task": ResumeTaskCommand,
}
