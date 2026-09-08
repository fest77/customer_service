"""
这个模块作用
    创建远程调用httpx工具类
"""
import asyncio

from httpx import AsyncClient

# import requests
# result = requests.get("http://127.0.0.1:18081/users/u1001/orders")

# 1 定义变量 异步
http_client: AsyncClient | None = None

# 2 创建两个方法，
# 初始化方法
def init_http_client():
    global http_client
    http_client = AsyncClient(timeout=10.0)

# 关闭的方法
async def close_http_client():
    # 异步
    await http_client.aclose()

# 测试方法
async def test():
    init_http_client()
    # restful风格： 查询get  添加post   修改put   删除delete
    result = await http_client.get("http://127.0.0.1:18081/users/u1001/orders")
    print(result.json())

if __name__ == "__main__":
    asyncio.run(test())
