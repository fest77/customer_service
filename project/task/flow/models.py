from dataclasses import dataclass, field
from project.task.flow.steps import FlowStep, StartFlowStep

@dataclass
class FlowSlot:
    name: str
    type: str = "any"
    label: str = ""
    description: str = ""

@dataclass
class Flow:
    id: str
    description: str = ""
    steps: list[FlowStep] = field(default_factory=list)
    slots: list[FlowSlot] = field(default_factory=list)
    name: str | None = None

    # 获取开始类型步骤数据
    def get_start_step(self)->StartFlowStep:
        for step in self.steps:
            # 判断 开始类型
            if isinstance(step, StartFlowStep):
                return step
        raise Exception("Flow not found")

    # 根据步骤id获取步骤对应数据
    def get_step_by_id(self, step_id)->FlowStep:
        for step in self.steps:
            if step.id == step_id:
                return step
        raise Exception("step not found")

@dataclass
class FlowCatalog:
    flows: dict[str, Flow] = field(default_factory=dict)
    slots: dict[str, FlowSlot] = field(default_factory=dict)

    # 根据流程id获取流程
    def get_flow_by_id(self, flow_id)->Flow:
        return self.flows[flow_id]


