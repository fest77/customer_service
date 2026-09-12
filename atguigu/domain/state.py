import time
import uuid
from dataclasses import dataclass, field


from atguigu.domain.message import UserMessage, BotMessage
from atguigu.task.lifecycle.models import TaskEvent, TaskRef, TaskSwitched, TaskStarted, TaskCanceled


# 一轮对话，一个问题对应一个或者多个回答
@dataclass
class Turn:
    turn_id: str
    # 用户提问
    user_message: UserMessage
    # 客服回复
    bot_message: list[BotMessage]=field(default_factory=list)

# 会话对象
@dataclass
class Session:
    # session的id，区别不同session
    session_id: str
    # session创建时间戳
    started_at: float
    # session最后一次活跃时间
    last_activity_at: float
    # 关闭时间
    closed_at: float | None = None
    # 每个session会话多轮对话
    turns:list[Turn]=field(default_factory=list)

# 对象类型消息
@dataclass
class FocusedObject:
    type:str
    id:str
    title:str | None=None
    attributes:dict=field(default_factory=dict)

# 三种能力都有数据：任务流程、知识问答、闲聊
@dataclass
class SharedState:
    # 对象类型消息
    focused_object: FocusedObject | None = None
    # 多个会话数据
    sessions: list[Session] = field(default_factory=list)

    # 创建新session
    def create_session(self):
        # 获取当前时间
        now = time.time()
        session = Session(
            session_id=str(uuid.uuid4()),
            started_at=now,
            last_activity_at=now,
        )
        # 创建session对象放到state里面
        self.sessions.append(session)

    # 关闭当前session
    def close_current_session(self):
        self.sessions[-1].closed_at = time.time()


# 某个任务流程步骤相关数据
@dataclass
class TaskInstance:
    # 流程id，对应yaml文件  refund_request
    flow_id: str
    # 步骤id ,比如 start
    step_id: str | None = None
    # 当前任务id
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # task_id: str | None = None
    # 槽位数据字典  {order_number : a10098765}
    slots: dict= field(default_factory=dict)

    # 返回TaskRef
    def to_ref(self)->TaskRef:
        return TaskRef(
            flow_id=self.flow_id,
            task_id=self.task_id,
        )

# 任务流程特有数据，流程步骤数据
@dataclass
class TaskState:
    # 当前正在运行（活跃）的任务
    active: TaskInstance | None = None
    # 中断（暂停）的任务
    paused: list[TaskInstance] = field(default_factory=list)

    # 处理start_flow数据更新
    def start(self,task:TaskInstance)->TaskEvent:
        # 1 判断当前是否活跃任务
        # 如果有，把活跃任务放到中断列表里面，把当前 任务变成活跃任务
        if self.active:
            # 暂停任务
            previous = self.active.to_ref()
            # 把活跃任务放到中断列表里面
            self.paused.append(self.active)

            # 把当前 任务变成活跃任务
            self.active = task

            current = self.active.to_ref()

            return TaskSwitched(
                previous=previous,
                current=current,
            )
        else:
            # 如果没有，把当前 任务变成活跃任务
            self.active = task
            return TaskStarted(
                task=self.active.to_ref()
            )

    # {"command": "cancel_task", "task_id": "<task_id>"}
    def cancel(self, task_id:str)->TaskEvent:
        # 1 判断当前活跃任务 是否要取消任务
        # 是
        # if self.active:
        if self.active.task_id == task_id:
            canceled_task = self.active.to_ref()
            # 是，把当前活跃任务取消
            self.active = None
            return TaskCanceled(
                task = canceled_task
            )
        # 不是，根据任务id到中断列表找任务，找到的话，从中断列表删除任务
        else:
            # 遍历中断列表
            for paused_task in self.paused:
                if paused_task.task_id == task_id:
                    canceled_task = paused_task.to_ref()
                    # 取消任务从中断列表删除
                    self.paused.remove(paused_task)

                    return TaskCanceled(
                        task=canceled_task
                    )
            raise ValueError("取消任务不存在")

    # {"command": "resume_task", "task_id": "<task_id>"}
    def resume(self, task_id:str)->TaskEvent:
        resume_task_ref = None
        resume_task =  None
        # 从中断列表获取要恢复任务
        for index,task in enumerate(self.paused):
            if task.task_id == task_id:
                # 从中断列表取出来恢复任务
                resume_task = self.paused.pop(index)
                resume_task_ref = resume_task.to_ref()
                break
        if resume_task is None:
            raise ValueError("恢复任务不存在")

        # 判断当前是否活跃任务，如果没有直接把恢复任务变成活跃任务
        #   如果有活跃任务：当前活跃任务暂停，把恢复任务变成活跃任务
        if self.active:
            previous = self.active.to_ref()
            # 当前活跃任务暂停
            self.paused.append(self.active)
            # 把恢复任务变成活跃任务
            self.active = resume_task

            return TaskSwitched(
                previous=previous,
                current=resume_task_ref
            )
        else:# 如果没有直接把恢复任务变成活跃任务
            self.active = resume_task
            return TaskStarted(
                task=resume_task_ref
            )

@dataclass
class DialogueState:
    # 用户id
    sender_id: str
    # 三种能力都有数据：任务流程、知识问答、闲聊
    shared: SharedState=field(default_factory=SharedState)
    # 任务流程特有数据，流程步骤数据
    tasks: TaskState=field(default_factory=TaskState)