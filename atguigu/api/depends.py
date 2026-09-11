from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu import repository
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.plan.turn_plan import TurnPlanner
from atguigu.plan.turn_plan_validation import TurnPlannValidator
from atguigu.repository.dialogue_repository import DialogueRepository
from atguigu.service.dialogue_service import DialogueService
from atguigu.utils import database

"""
   api  --  service  --  repository -- session
               |
            engine -- ？
"""

# 数据库操作session对象
async def get_session():
    async with database.async_session() as session:
        # 暂停
        yield session

# 创建repository
async def get_repository(
        session:AsyncSession=Depends(get_session)):

    return DialogueRepository(session=session)

#创建engine对象
async def get_engine():
    turn_planner = TurnPlanner()
    turn_plann_validator = TurnPlannValidator()
    return DialogueEngine(
        turn_planner=turn_planner,
        turn_plann_validator=turn_plann_validator
    )

async def get_dialogue_service(
        dialogue_repository:DialogueRepository=Depends(get_repository),
        dialogue_engine:DialogueEngine=Depends(get_engine)):
    return DialogueService(
        engine=dialogue_engine,
       repository=dialogue_repository
    )