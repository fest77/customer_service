from dataclasses import dataclass

@dataclass
class FlowStepLink:
    target: str

@dataclass
class StaticLink(FlowStepLink):
    pass

@dataclass
class ConditionalLink(FlowStepLink):
    condition: str

@dataclass
class FallbackLink(FlowStepLink):
    pass