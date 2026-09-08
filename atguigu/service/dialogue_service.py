"""
当前这个模块，推进业务的
"""
class DialogueService:
    pass
"""
  1 根据api层传递sender_id，调用repository层查询当前用户历史会话记录
  2 根据查询历史记录 + 用户问题 调用engine层处理用户消息
  3 把当前这一次对话，调用repository层保存数据库里面
  4 返回engine层处理结果
"""