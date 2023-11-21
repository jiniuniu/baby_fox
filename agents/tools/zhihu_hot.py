from typing import Optional, Type

import requests
from cachetools.func import ttl_cache
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.base import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

ZHIHU_HOT_EVENTS_API = "https://api.zhihu.com/topstory/hot-lists/total"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


@ttl_cache()
def get_zhihu_hot_events():
    logger.info("get_zhihu_hot_events called")
    params = {"limit": "10", "is_browser_model": "0"}
    res = requests.get(
        url=ZHIHU_HOT_EVENTS_API,
        headers=HEADERS,
        params=params,
    )
    if res.status_code != 200:
        logger.error(f"HTTP response error: {res}")
        return []
    res = res.json()
    hot_lists = []
    for data in res["data"]:
        title = data["target"]["title"]
        url = data["target"]["url"].replace(
            "api.zhihu.com/questions", "zhihu.com/question"
        )
        excerpt = data["target"]["excerpt"]
        hot_lists.append(
            {
                "title": title,
                "url": url,
                "excerpt": excerpt,
            }
        )
    return hot_lists


class ZhihuHotEventsInput(BaseModel):
    query: str = Field("", description="query to look up for hot event list.")


class ZhihuHotEventsTool(BaseTool):
    """Tool that you can get up-to-date hot events list from zhihu."""

    name: str = "zhihu_hot_list"

    description: str = """实时更新的知乎的热榜，可以对当前发生的热点事件进行查询的工具，
    返回的结果是一个列表，每个元素包含热点的标题（title），热点的描述（excerpt）和链接（url）
    """
    args_schema: Type[BaseModel] = ZhihuHotEventsInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_events = get_zhihu_hot_events()
        res = ""
        for idx, event in enumerate(hot_events):
            title = event["title"]
            excerpt = event["excerpt"]
            url = event["url"]
            res += f"{idx + 1}\n"
            res += f"标题：{title}\n简介：{excerpt}\n链接：{url}\n\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")
