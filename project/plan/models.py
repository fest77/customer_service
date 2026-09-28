from dataclasses import dataclass, field
from enum import Enum

from project.task.command.models import Command

# plan / models.py
@dataclass
class TaskTurnPlan:
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, task_data: dict) -> "TaskTurnPlan":
        return cls(commands=[Command.from_dict(command_data)
                 for command_data in task_data['commands']])


@dataclass
class KnowledgeTurnPlan:
    intents: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, knowledge_data: dict) -> "KnowledgeTurnPlan":
        return KnowledgeTurnPlan(knowledge_data['intents'])


@dataclass
class ChitchatTurnPlan:
    pass


@dataclass
class TurnPlan:
    task: TaskTurnPlan | None = None
    knowledge: KnowledgeTurnPlan | None = None
    chitchat: ChitchatTurnPlan | None = None

    @classmethod
    def from_dict(cls, plan_data: dict) -> "TurnPlan":
        return cls(
            task=TaskTurnPlan.from_dict(plan_data['task'])
                if plan_data['task'] is not None else None,

            knowledge=KnowledgeTurnPlan.from_dict(plan_data['knowledge'])
                         if plan_data['knowledge'] is not None else None,

            chitchat=ChitchatTurnPlan()
                       if plan_data['chitchat'] is not None else None
        )


class ClarifyReason(Enum):
    MISSING_TRACK = "missing_track"
    MULTIPLE_TRACKS = "multiple_tracks"
    MISSING_TASK_COMMANDS = "missing_task_commands"
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"
    MISSING_FOCUSED_OBJECT = "missing_focused_object"
    OBJECT_REQUIRES_INTENT = "object_requires_intent"
    INVALID_TASK_COMMAND = "invalid_task_command"
    UNKNOWN_KNOWLEDGE_INTENT = (
        "unknown_knowledge_intent"
    )

@dataclass
class TurnPlanValidationResult:
    # 校验成功 true  校验失败 false
    valid: bool
    # 校验失败：失败原因
    reason: ClarifyReason | None = None
