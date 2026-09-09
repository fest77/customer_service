"""
当前这个模块用于操作数据库
"""
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState

# 序列化和反序列化
## 对象 ==》 json字符串   dump_json
## json字符串 ==》 对象   validate_json
# 在pydantic模块里面，使用类型适配器实现 序列化和反序列化
DIALOGUE_STATE_ADAPTER = TypeAdapter(DialogueState)

class DialogueRepository:

    def __init__(self,session:AsyncSession):
        self.session = session

    # 1 根据sender_id查询
    # 查询数据库返回json字符串 ，把json字符串转换对象
    async def load_state(self, sender_id):
        pass

    # 2 保存数据
    # 把对象转换字符串，保存数据库
    async def save_state(self, state):
        pass