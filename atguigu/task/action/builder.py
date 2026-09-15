from atguigu.task.action.custom.lookup_logistics import LookupLogistics
from atguigu.task.action.custom.lookup_order_status import LookupOrderStatus
from atguigu.task.action.registry import ActionRegistry

# 下面这个方法在depends模块完成注入关系
# 调用ActionRegistry方法完成action注册
# todo 后续完善，改造自动注册
def registry_action(registry:ActionRegistry):
    registry.register_action(LookupLogistics())
    registry.register_action(LookupOrderStatus())