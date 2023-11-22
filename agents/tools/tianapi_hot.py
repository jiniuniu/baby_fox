from enum import Enum
from typing import Optional, Type

import requests
from cachetools.func import ttl_cache
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.base import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

from server.config import env_settings

HEADERS = {"Content-type": "application/x-www-form-urlencoded"}


# 微博热搜
WEIBO_HOT_URL = "https://apis.tianapi.com/weibohot/index"
# 微信热搜
WX_HOT_URL = "https://apis.tianapi.com/wxhottopic/index"
# 全网热搜
NETWORK_HOT_URL = "https://apis.tianapi.com/networkhot/index"
# 抖音热搜
DOUYIN_HOT_URL = "https://apis.tianapi.com/douyinhot/index"
# 头条热搜
TOUTIAO_HOT_URL = "https://apis.tianapi.com/toutiaohot/index"
# 百度热搜
BAIDU_HOT_URL = "https://apis.tianapi.com/nethot/index"


@ttl_cache()
def get_response_from_url(url: str):
    try:
        response = requests.get(
            url,
            timeout=5,
            params={"key": env_settings.TIAN_API_KEY},
            headers=HEADERS,
        )
        response.raise_for_status()
        res_json = response.json()
        hot_list = res_json["result"]["list"]
        return hot_list
    except Exception as e:
        logger.error(f"error {e}")
        return []


class HotListInput(BaseModel):
    query: str = Field("", description="query to look up for hot event list.")


class WeiboHotListTool(BaseTool):
    name: str = "weibo_hot_list"
    chinese_name: str = "微博热搜"

    description: str = """实时更新微博热搜，可以对当前微博上的热搜的短语进行查询的工具，
    返回的结果是一个列表，每个元素包含热搜的短语。
    """
    args_schema: Type[BaseModel] = HotListInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_list = get_response_from_url(WEIBO_HOT_URL)
        res = ""
        for idx, data in enumerate(hot_list):
            hot_word = data["hotword"]
            res += f"{idx + 1}. {hot_word}\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")


class WXHotListTool(BaseTool):
    name: str = "wx_hot_list"
    chinese_name: str = "微信热搜"

    description: str = """实时更新微信热搜，可以对当前微信公众平台热点话题进行查询的工具，
    返回的结果是一个列表，每个元素包含热点话题的短语。
    """
    args_schema: Type[BaseModel] = HotListInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_list = get_response_from_url(WX_HOT_URL)
        res = ""
        for idx, data in enumerate(hot_list):
            hot_word = data["word"]
            res += f"{idx + 1}. {hot_word}\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")


class NetworkHotListTool(BaseTool):
    name: str = "network_hot_list"
    chinese_name: str = "全网热搜"

    description: str = """实时更新全网热搜，可以对全网热点话题进行查询的工具，
    返回的结果是一个列表，每个元素包含热点话题的短语。
    """
    args_schema: Type[BaseModel] = HotListInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_list = get_response_from_url(NETWORK_HOT_URL)
        res = ""
        for idx, data in enumerate(hot_list):
            hot_word = data["title"]
            res += f"{idx + 1}. {hot_word}\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")


class DouyinHotListTool(BaseTool):
    name: str = "douyin_hot_list"
    chinese_name: str = "抖音热搜"

    description: str = """实时更新抖音热搜，可以对抖音热点话题进行查询的工具，
    返回的结果是一个列表，每个元素包含热点话题的短语。
    """
    args_schema: Type[BaseModel] = HotListInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_list = get_response_from_url(DOUYIN_HOT_URL)
        res = ""
        for idx, data in enumerate(hot_list):
            hot_word = data["word"]
            res += f"{idx + 1}. {hot_word}\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")


class ToutiaoHotListTool(BaseTool):
    name: str = "toutiao_hot_list"
    chinese_name: str = "头条热搜"

    description: str = """实时更新头条的热搜，可以对头条热点话题进行查询的工具，
    返回的结果是一个列表，每个元素包含热点话题的短语。
    """
    args_schema: Type[BaseModel] = HotListInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_list = get_response_from_url(TOUTIAO_HOT_URL)
        res = ""
        for idx, data in enumerate(hot_list):
            hot_word = data["word"]
            res += f"{idx + 1}. {hot_word}\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")


class BaiduHotListTool(BaseTool):
    name: str = "baidu_hot_list"
    chinese_name: str = "百度热搜"

    description: str = """实时更新百度热搜，可以对百度热搜的话题进行查询的工具，
    返回的结果是一个列表，每个元素包含热点话题的短语。
    """
    args_schema: Type[BaseModel] = HotListInput

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        hot_list = get_response_from_url(BAIDU_HOT_URL)
        res = ""
        for idx, data in enumerate(hot_list):
            hot_word = data["keyword"]
            res += f"{idx + 1}. {hot_word}\n"
        return res

    def _arun(self, query: str):
        raise NotImplementedError("error here")


if __name__ == "__main__":
    res = get_response_from_url(NETWORK_HOT_URL)
    logger.info(res)
