import uvicorn

from atguigu.config.config import settings
from atguigu.utils.database import init_db_engine
from atguigu.utils.http_client import init_http_client

# 进程
if __name__=="__main__":
    # reload=True init_db_engine()没有生效
    init_db_engine()
    init_http_client()
    uvicorn.run("atguigu.api.app:app",
                host=settings.app_host,
                port=settings.app_port,)