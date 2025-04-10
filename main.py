import asyncio
from collections.abc import Iterator
from textwrap import dedent
import uuid
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.mcp import MCPTools
from agno.workflow import Workflow
from dotenv import load_dotenv
import os
from agno.workflow import RunResponse
from agno.storage.sqlite import SqliteStorage

load_dotenv()


class TravelAgent(Workflow):
    """自定义的高德地图查询智能体，可以查询路线、路况、天气、限行等信息，生成 html 页面"""

    description = dedent("""\
        一个高德地图查询智能体，可以查询路线、路况、天气、限行等信息，生成路线报告。
        生成markdown格式报告具有热门景点的介绍，观光建议，按照时间顺序合理划分每个景点行程规划，中间穿插美食推荐，住宿建议。
        再结合 iconify 和 unsplash 替换不同样式，采用现代化渐变配色，生成现代化、简约美观的 html 页面供用户查看
""")

    amap_tools = MCPTools(
        component_id="npx -y @amap/amap-maps-mcp-server",
        env={
            "AMAP_MAPS_API_KEY": os.getenv("AMAP_KEY"),
        },
    )

    plan_agent = Agent(
        model=DeepSeek(
            id="Pro/deepseek-ai/DeepSeek-V3",
            base_url=os.getenv("MODEL_BASE_URL"),
            api_key=os.getenv("MODEL_API_KEY"),
        ),
        tools=[amap_tools],
        description="""
        您是一位资深旅行规划师，擅长根据用户需求生成旅行规划报告。
        您规划的行程中包括路线规划、景点介绍、美食推荐、住宿建议等。
        """,
        introduction=dedent("""\
        1、天气查询
        - 查询今天具体日期
        - 输入城市名称，查询该城市今天至未来7天的天气情况
        2、路线规划
        - 规划每个景点的出行路线，两个景点之间相承接
        - 避开拥堵路段，避开限行路段
        - 中午、晚上休息时间，穿插美食推荐
        3、景点介绍
        - 根据景点名称，查询景点介绍，包括景点地址、开放时间、门票价格、景点特色等
        4、住宿建议
        - 根据景点名称，查询周边住宿信息，包括酒店名称、地址、价格、星级等
        - 根据用户预算，推荐性价比高的酒店
        """),
        markdown=True,
    )

    def run(self, question: str):
        asyncio.run(self.amap_tools.initialize())
        self.plan_agent.print_response(question, stream=True)


# def main():
#     agent = Agent(
#         model=DeepSeek(
#             id="Pro/deepseek-ai/DeepSeek-V3",
#             base_url="https://api.siliconflow.cn/v1",
#             api_key="sk-nrtetzxcesggjjftpeqryxlfkeywajgnboaecywmmarbhzrq",
#         ),
#         tools=[DuckDuckGoTools()],
#         markdown=True,
#     )
#     agent.print_response("What's happening in New York?", stream=True)


if __name__ == "__main__":
    import random

    from rich.prompt import Prompt

    # Fun example prompts to showcase the generator's versatility
    example_prompts = [
        "请为我规划深圳旅游路线",
        "我准备去天津旅行，请帮我规划路线",
        "我准备去北京旅行，请帮我规划路线",
        "我准备去上海旅行，请帮我规划路线",
        "我准备去广州旅行，请帮我规划路线",
        "我准备去深圳旅行，请帮我规划路线",
        "我准备去成都旅行，请帮我规划路线",
        "我准备去重庆旅行，请帮我规划路线",
        "我准备去西安旅行，请帮我规划路线",
        "我准备去杭州旅行，请帮我规划路线",
        "我准备去南京旅行，请帮我规划路线",
        "我准备去武汉旅行，请帮我规划路线",
        "我准备去长沙旅行，请帮我规划路线",
    ]

    # Get topic from user
    topic = Prompt.ask(
        "[bold]Enter a blog post topic[/bold] (or press Enter for a random example)\n✨",
        default=random.choice(example_prompts),
    )

    # Initialize the blog post generator workflow
    # - Creates a unique session ID based on the topic
    # - Sets up SQLite storage for caching results
    generate_travel_post = TravelAgent(
        session_id=f"generate-travel-post-on-{uuid.uuid4()}",
        storage=SqliteStorage(
            table_name="generate_travel_post_workflows",
            db_file="tmp/agno_workflows.db",
        ),
        debug_mode=True,
    )

    generate_travel_post.run(question=topic)
