import importlib
import inspect
import pkgutil

from atguigu.task.action.base import Action
from atguigu.task.action.custom.lookup_logistics import LookupLogistics
from atguigu.task.action.custom.lookup_order_status import LookupOrderStatus
from atguigu.task.action.registry import ActionRegistry

# 下面这个方法在depends模块完成注入关系
# 调用ActionRegistry方法完成action注册

def registry_action(registry:ActionRegistry):
    registry.register_action(LookupLogistics())
    registry.register_action(LookupOrderStatus())

# 包扫描的自动注册
def auto_registry_action(registry:ActionRegistry):
    # 1 加载action所在的包
    package = importlib.import_module(
        'atguigu.task.action.custom')

    # 获取加载的包所有的内容，从所有内容获取模块
    ## 从模块获取Action的子类
    for _,module_name,is_package in pkgutil.iter_modules(package.__path__,
                  prefix=f"{package.__name__}."):
        # 判断是否包
        if is_package:
            continue

        # 如果不是包，是模块 py文件，每个模块有属性 方法 类（获取）
        module = importlib.import_module(module_name)

        for _,action_class in inspect.getmembers(module, inspect.isclass):
            # 类是Action子类
            # 获取Action子类，实现注册
            if not issubclass(action_class, Action) or action_class is Action:
                continue

            # action子类必须是当前包模块里面类，如果import进来不能注册
            if action_class.__module__ != module.__name__:
                continue

            registry.register_action(action_class())