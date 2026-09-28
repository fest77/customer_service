"""
当前这个模块，推进业务的
"""
from project.domain.message import UserMessage, ProcessResult, BotMessage
from project.domain.state import DialogueState
from project.engine.dialogue_engine import DialogueEngine
from project.repository.dialogue_repository import DialogueRepository


class DialogueService:

    def __init__(self,engine:DialogueEngine,
                 repository:DialogueRepository):
        self.engine = engine
        self.repository = repository

    """
      1 根据api层传递sender_id，调用repository层查询当前用户历史会话记录
      2 根据查询历史记录 + 用户问题 调用engine层处理用户消息
      3 把当前这一次对话，调用repository层保存数据库里面
      4 返回engine层处理结果
    """
    async def process_message(self, user_message:UserMessage)->ProcessResult:
        # 1 根据api层传递sender_id，调用repository层查询当前用户历史会话记录
        sender_id = user_message.sender_id
        state:DialogueState= await self.repository.load_state(sender_id)

        # 2 根据查询历史记录 + 用户问题 调用engine层处理用户消息
        process_result:ProcessResult = \
            await self.engine.process_message(state,user_message)

        # 3 把当前这一次对话，调用repository层保存数据库里面
        await self.repository.save_state(state)

        # todo 4 返回engine层处理结果
        return process_result
        # return ProcessResult(
        #     sender_id=sender_id,
        #     message_id=user_message.message_id,
        #     messages=[BotMessage(
        #         text="hello",
        #         object=None
        #     )]
        # )

    async def get_history_info(self, sender_id):
        return await self.repository.load_state(sender_id)
