from dataclasses import dataclass
from enum import Enum


class ResponseMode(Enum):
    # 直接返回text内容
    STATIC = "static"

    # 基于text内容，调用llm，把text修改返回
    # REPHRASE = "rephrase"
    # 直接llm生成内容 返回
    # GENERATE = "generate"


@dataclass
class ResponseTemplate:
    mode: ResponseMode = ResponseMode.STATIC
    text: str | None = None
    prompt: str | None = None

    ###########
    @classmethod
    def from_dict(cls,template_data:dict
                    )->"ResponseTemplate":
        return cls(
            mode=ResponseMode.STATIC,
            text=template_data.get('text'),
            prompt=template_data.get('prompt') )


