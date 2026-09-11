"""
这个模块用于加载yaml文件，封装到FlowCatalog
"""
from pathlib import Path

import yaml

from atguigu.task.flow.models import FlowCatalog, FlowSlot, Flow
from atguigu.task.flow.steps import FlowStep


class FlowLoader:
    # 根据yaml文件路径加载yaml文件数据，封装到FlowCatalog对象
    def load(self,path:Path)->FlowCatalog:
        # read_text读取 文件内容，返回文本
        flow_text = path.read_text(encoding='utf-8')
        # 把读取文本解析字典格式  代码注入
        flow_dict = yaml.safe_load(flow_text)

        # flow_dict ==》 FlowCatalog
        # 加载槽位数据
        slots:dict[str,FlowSlot] = self._load_slots(flow_dict['slots'])

        # 加载流程数据
        flows: dict[str, Flow] = self._load_flows(flow_dict['flows'],slots)

        return FlowCatalog(slots=slots,
                           flows=flows)

    # 加载yaml所有槽位数据
    def _load_slots(self, slots_data:dict[str, dict])->dict[str,FlowSlot]:
        slots: dict[str, FlowSlot] = {}
        # 遍历slots_data字典
        for slot_name,slot_data in slots_data.items():
            # 根据slot_name，把对应slot_data ==》 FlowSlot
            slots[slot_name] = FlowSlot(
                name=slot_name,
                **slot_data,
            )
        return slots

    # 加载yaml所有流程数据
    def _load_flows(self, flow_data:dict[str, dict],
                         slots:dict[str,FlowSlot]) -> dict[str,Flow]:
        flows: dict[str,Flow] = {}
        # 遍历flow_data字典
        for flow_id,flow_data in flow_data.items():
            # 槽位数据
            flow_slots: list[FlowSlot] = [
             slots[collect_step['slot_name']]
            for collect_step in flow_data['steps']
             if collect_step['type'] == 'collect']

            # 步骤
            steps:list[FlowStep] = [
                FlowStep.from_dict(flow_step)
               for flow_step in  flow_data['steps']
            ]

            flow:Flow = Flow(
                id=flow_id,
                description=flow_data['description'],
                steps=steps,
                slots=flow_slots,
                name=flow_data['name'],
            )
            flows[flow_id] = flow
        return flows

if __name__=='__main__':
    loader = FlowLoader()
    path = Path(__file__).parents[3]/'flow_config'/'user_flows.yml'
    res = loader.load(path)
    print(res)