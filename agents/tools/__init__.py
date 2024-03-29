from typing import List

from langchain.agents.tools import BaseTool

from agents.tools.holiday_ad_searcher import HolidayAdSearchTool
from agents.tools.martech_kb import BeautiCareCaseSearchTool, MaternalToyCaseSearchTool
from agents.tools.searcher import BabyFoxSearchTool
from agents.tools.tianapi_hot import (
    BaiduHotListTool,
    DouyinHotListTool,
    NetworkHotListTool,
    ToutiaoHotListTool,
    WeiboHotListTool,
    WXHotListTool,
)
from agents.tools.zhihu_hot import ZhihuHotEventsTool

all_tools: List[BaseTool] = [
    MaternalToyCaseSearchTool(),
    BeautiCareCaseSearchTool(),
    ZhihuHotEventsTool(),
    BaiduHotListTool(),
    DouyinHotListTool(),
    NetworkHotListTool(),
    ToutiaoHotListTool(),
    WeiboHotListTool(),
    WXHotListTool(),
    HolidayAdSearchTool(),
    BabyFoxSearchTool(),
]


TOOL_MAP = {}
for tool in all_tools:
    TOOL_MAP[tool.chinese_name] = tool
