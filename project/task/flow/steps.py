from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from project.task.flow.links import FlowStepLink, StaticLink, ConditionalLink, FallbackLink
from project.task.response.models import ResponseTemplate

class FlowStepType(Enum):
    START = "start"
    ACTION = "action"
    RESPONSE = "response"
    COLLECT = "collect"
    END = "end"

@dataclass
class FlowStep:
    id: str
    type: FlowStepType
    next: list[FlowStepLink] = field(default_factory=list)
    description: str = ""

    # {id:start , type: start}
    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "FlowStep":
        # start
        flow_type = flow_step_data['type']
        # type= start   得到类 StartFlowStep
        clz = TYPE_TO_STEP_CLASS[flow_type]
        # StartFlowStep.from_dict(flow_step_data)
        return clz.from_dict(flow_step_data)


    @classmethod
    def base_fields(cls, flow_step_data: dict[str, Any]) -> dict[str, Any]:
        return {
            'id': flow_step_data['id'],
            'type': FlowStepType(flow_step_data['type']),
            'description': flow_step_data.get('description', ''),
            'next': cls._build_links(flow_step_data['next'])
        }

    @classmethod
    def _build_links(cls, next_data: str | list[dict]) -> list[FlowStepLink]:
        # next值字符串，无条件跳转
        if isinstance(next_data, str):
            return [StaticLink(target=next_data)]
        else:# 有条件跳转
            link_list: list[FlowStepLink] = []
            for link_data in next_data:
                if 'if' in link_data:
                    link_list.append(ConditionalLink(condition=link_data['if'], target=link_data['then']))
                else:
                    link_list.append(FallbackLink(target=link_data['else']))
            return link_list

@dataclass
class StartFlowStep(FlowStep):
    # 前向引用
    # {a:1,b:2} == StartFlowStep对象
    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "StartFlowStep":
        return cls(**FlowStep.base_fields(flow_step_data))

@dataclass
class ActionFlowStep(FlowStep):
    action: str = ""
    args: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "ActionFlowStep":
        return cls(
            **FlowStep.base_fields(flow_step_data),
            action=flow_step_data['action'],
            args=flow_step_data.get('args', {})
        )

@dataclass
class ResponseFlowStep(FlowStep):
    template: ResponseTemplate = field(default_factory=ResponseTemplate)

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "ResponseFlowStep":
        # todo: 加载逻辑
        # pass
        return cls(
            **FlowStep.base_fields(flow_step_data),
            template=ResponseTemplate.from_dict(
                        flow_step_data['template'])
        )

@dataclass
class CollectSlotStep(FlowStep):
    slot_name: str = ""
    template: ResponseTemplate = field(default_factory=ResponseTemplate)

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "CollectSlotStep":
        # 加载逻辑
        return cls(
            **FlowStep.base_fields(flow_step_data),
            slot_name=flow_step_data['slot_name'],
            template=ResponseTemplate.from_dict(flow_step_data['template'])
        )

@dataclass
class EndFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, flow_step_data: dict[str, Any]) -> "EndFlowStep":
        return cls(**FlowStep.base_fields(flow_step_data))

TYPE_TO_STEP_CLASS = {
    'start': StartFlowStep,
    'collect': CollectSlotStep,
    'response': ResponseFlowStep,
    'action': ActionFlowStep,
    'end': EndFlowStep
}
