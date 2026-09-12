from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class TaskRef:
    task_id: str
    flow_id: str

# 开始任务变化
@dataclass
class TaskStarted:
    task: TaskRef

# 切换任务变化
@dataclass
class TaskSwitched:
    previous: TaskRef
    current: TaskRef

# 恢复任务变化
@dataclass
class TaskResumed:
    task: TaskRef

# 取消任务变化
@dataclass
class TaskCanceled:
    task: TaskRef

# def  test() -> TaskCanceled | TaskResumed | TaskSwitched
# def test1() -> TaskEvent

TaskEvent: TypeAlias = (
        TaskStarted
        | TaskSwitched
        | TaskResumed
        | TaskCanceled
)