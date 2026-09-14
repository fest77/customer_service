"""
这个模块作用
 response类型步骤 数据渲染

"""
from jinja2 import Template

from atguigu.domain.message import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.response.models import ResponseTemplate, ResponseMode


class ResponseTemplateRender:
    # 渲染
    def render_response(self,
                template:ResponseTemplate,
                        state:DialogueState)->BotMessage:
        # jinja2
        if template.mode == ResponseMode.STATIC:
            template_obj = Template(template.text)
            render_text = template_obj.render(slots=state.tasks.active.slots)

            return BotMessage(text=render_text)

        if template.mode == ResponseMode.REPHRASE:
            # 调用LLM，把返回内容由LLM修改，修改之后返回用户
            pass

        if template.mode == ResponseMode.GENERATE:
            # 直接调用LLM，根据提示生成返回内容
            pass