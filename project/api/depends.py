from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from project import repository
from project.chitchat import chit_chat
from project.chitchat.chit_chat import ChitChat
from project.clarify.clarify_response import ClarifyResponse
from project.engine.dialogue_engine import DialogueEngine
from project.knowledge.hanlder import KnowledgeHanlder
from project.knowledge.provider import ProductProvider, RAGProvider, ApiOrderProvider, FAQProvider
from project.knowledge.registry import KnowledgeProviderRegistry
from project.knowledge.responder import KnowledgeResponseder
from project.plan.turn_plan import TurnPlanner
from project.plan.turn_plan_validation import TurnPlannValidator
from project.repository.dialogue_repository import DialogueRepository
from project.service.dialogue_service import DialogueService
from project.task.action.builder import registry_action
from project.task.action.registry import ActionRegistry
from project.task.action.runner import ActionRunner
from project.task.command.processor import CommandProcessor
from project.task.flow.executor import FlowExecutor
from project.task.handler import TaskHandler
from project.task.lifecycle.responder import TaskLifecycleResponder
from project.task.response.renderer import ResponseTemplateRender
from project.utils import database

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

    # registry
    registry = ActionRegistry()
    # 调用方法注册action对象到字典里面
    registry_action(registry)
    # action_runner
    action_runner = ActionRunner(
        registry = registry
    )
    # flow_executor
    flow_executor = FlowExecutor(
        response_render = ResponseTemplateRender(),
        action_runner = action_runner
    )

    task_handler = TaskHandler(
        command_processor=CommandProcessor(),
        task_lifecycle=TaskLifecycleResponder(),
        flow_executor = flow_executor
    )

    clarif_response = ClarifyResponse()
    chit_chat=ChitChat()

    knowledge_registry=KnowledgeProviderRegistry([
            ProductProvider(),
            ApiOrderProvider(),
            FAQProvider(),
            RAGProvider()
        ]
    )

    knowledge_handler = KnowledgeHanlder(
        know_responseder=KnowledgeResponseder(),
        knowledge_registry=knowledge_registry
    )

    return DialogueEngine(
        turn_planner=turn_planner,
        turn_plann_validator=turn_plann_validator,
        task_handler=task_handler,
        clarif_response=clarif_response,
        chit_chat=chit_chat,
        knowledge_handler=knowledge_handler
    )

async def get_dialogue_service(
        dialogue_repository:DialogueRepository=Depends(get_repository),
        dialogue_engine:DialogueEngine=Depends(get_engine)):
    return DialogueService(
        engine=dialogue_engine,
       repository=dialogue_repository
    )