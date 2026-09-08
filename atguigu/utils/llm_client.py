"""
这个模块是工具模块
    创建llm对象
"""
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from atguigu.config.config import settings

llm:BaseChatModel = init_chat_model(
    # 模型名称
    model=settings.LLM_MODEL,
    model_provider = "openai",
    # api key  url
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    # 温度
    temperature=0
)

# 测试
if __name__ == "__main__":
    print(llm.invoke("hello").content)