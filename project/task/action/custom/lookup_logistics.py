"""
这个模块用于远程调用，调用中台接口查询物流信息
 查询物流信息，需要使用订单编号
"""
from project.config.config import settings
from project.domain.state import DialogueState
from project.task.action.base import Action, ActionResult
from project.utils import http_client

# 查询物流action
class LookupLogistics(Action):
    # name值和yaml文件查询物流流程action属性值相同
    name = "action_lookup_logistics"

    # 实现基类里面抽象方法，这个方法实现远程调用
    async def run(self,state:DialogueState)->ActionResult:
        # 获取查询订单编号
        order_number = state.tasks.active.slots.get("order_number")

        # 拼接中台查询物流接口地址
        url = (f"{settings.commerce_api_base_url}"
               f"/orders/{order_number}/logistics")

        # 远程调用
        response = await http_client.http_client.get(url)
        data = response.json().get("data","未知")

        return ActionResult(
            slot_updates={
                "logistics_company":data.get("logistics_company","未知公司"),
                "tracking_number":data.get("tracking_number","未知"),
                "logistics_status":data.get("status","未知")
            }
        )