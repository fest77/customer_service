from atguigu.config.config import settings
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.utils import http_client


# 查询订单状态
class LookupOrderStatus(Action):
    name = "action_lookup_order_status"

    async def run(self, state: DialogueState) -> ActionResult:
        # 获取订单编号
        order_number = state.tasks.active.slots.get("order_number")

        # 远程调用中台系统接口地址
        url = f"{settings.commerce_api_base_url}/orders/{order_number}/status"

        # 远程调用
        response = await http_client.http_client.get(url)
        data = response.json().get("data","未知")

        return ActionResult(
            slot_updates={
                "order_status":data.get("status","未知"),
                "order_summary":data.get("status_desc","未知")
            }
        )