"""
当前这个模块用于操作数据库
"""
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState
from atguigu.repository.orm.dialogue_state import DialogueStateRecord

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
    async def load_state(self, sender_id:str)->DialogueState:
        # sql实现
        # sql = "SELECT * FROM dialogue_states WHERE sender_id=:sid"
        # self.session.execute(sql,{"sid":sender_id})

        # orm实现
        ## 不需要编写sql语句，直接使用sqlalchemy封装的各种方法实现，依赖于orm数据模型
        sql = select(DialogueStateRecord).where(
                DialogueStateRecord.sender_id == sender_id)
        result = await self.session.execute(sql)
        record = result.scalar_one_or_none()
        if record: # 不为空
            # 因为查询表返回字符串，字符串转换 DialogueState对象
            # ## json字符串 ==》 对象   validate_json
            state = DIALOGUE_STATE_ADAPTER.validate_json(record.state_json)
            return state
        else:  # 为空
            return DialogueState(sender_id=sender_id)

    # 2 保存数据
    # 把对象转换字符串，保存数据库
    # ## 对象 ==》 json字符串   dump_json
    async def save_state(self, state:DialogueState):
        # 把state对象转换json字符串
        state_json = DIALOGUE_STATE_ADAPTER.dump_json(state).decode(encoding='utf-8')
        # 创建添加sql语句
        # sql语句 标准sql
        ## from sqlalchemy.dialects.mysql import insert
        # INSERT INTO dialogue_states(sender_id,state_json)
        #                            VALUES('1','abcd')
        sql = insert(DialogueStateRecord).values(sender_id=state.sender_id,
                                           state_json=state_json)

        # 判断表里面是否存在sender_id,
        # 如果存在，更新
        # 如果不存在，添加
        ## sqlalchemy.dialects.mysql封装上面实现
        on_duplicate_key = sql.on_duplicate_key_update(state_json=state_json)

        await self.session.execute(on_duplicate_key)
        await self.session.commit()
