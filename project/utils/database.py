"""
这个模块作用：
  封装操作mysql工具
"""
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine

from project.config.config import settings

# 1 定义两个变量
# 异步：引擎  session会话
engine: AsyncEngine | None = None
# async_sessionmaker工厂，通过这个工厂创建AsyncSession
async_session:async_sessionmaker[AsyncSession]

# 2 两个方法
# 初始化对象
def init_db_engine():
    global engine,async_session
    # 创建engine
    engine = create_async_engine(
        settings.database_url,
        echo=True, # 输出底层sql语句
    )
    # AsyncSession
    async_session = async_sessionmaker(
        engine,
        # 会话提交之后，内容对象数据是否过期
        expire_on_commit=False
    )

# 关闭方法
async def close_engine():
    await engine.dispose()

# 测试方法
async def test():
    init_db_engine()
    # 创建数据库连接，获取会话对象
    # async_session 工厂
    async with async_session() as session:
        result = await session.execute(text("select 1"))
        print(result.fetchone())
    await close_engine()

if __name__ == '__main__':
    asyncio.run(test())