"""
这个模块作用 把所有的provider注册到字典里面
为了根据位置找到对应provider对象
"""
from project.knowledge.provider import KnowledgeProvider


class KnowledgeProviderRegistry:

    # KnowledgeProviderRegistry实例化时候，把所有provider对象传入进来
    # provider_objs:list[KnowledgeProvider]代表所有provider对象
    def __init__(self,provider_objs:list[KnowledgeProvider]):
        # provider_objs遍历得到每个provider对象
        # 把每个provider对象放到字典里面  key是 provider对象provider_id属性
        #                             value是 provider对象
        # 字典名称 _providers_by_id
        self._providers_by_id = {
            provider_obj.provider_id : provider_obj
             for provider_obj in provider_objs
        }

    # 根据provider_id得到对应provider对象
    def get_provider_by_id(self,provider_id:str)->KnowledgeProvider:
        return self._providers_by_id[provider_id]
