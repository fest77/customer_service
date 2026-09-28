"""
这个模块作用：
    从环境变量中读取配置信息
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# from dotenv import load_dotenv
# load_dotenv()
# os.getenv("LLM_MODEL")

# 1 获取.env文件路径
## 获取相对路径，.env在当前路径上两层目录下
ENV_DIR = Path(__file__).parents[2]
ENV_FILE = ENV_DIR / ".env"

# 使用pydantic-settings方式读取配置
# 第一步 创建类，继承BaseSettings
# 第二步 使用封装方法读取env文件内容
class Settings(BaseSettings):
    # SettingsConfigDict有返回值，
    # 使用变量接收，变量名称固定的必须是model_config,约定
    model_config = SettingsConfigDict(
        # env文件路径
        env_file=ENV_FILE,
        # env文件编码
        env_file_encoding="utf-8",
        # 配置文件属性和类属性可以不一致
        extra="ignore"
    )

    # 和配置文件对应属性名称，不区分大小写
    LLM_MODEL: str = None
    llm_api_key: str
    llm_base_url: str
    # 数据库
    database_url: str
    # 商城 API
    commerce_api_base_url: str
    # 服务器
    app_host: str
    app_port: int

# 创建对象
settings = Settings()

if __name__ == '__main__':
    print(settings.LLM_MODEL)
    print(settings.app_host)





