import json
from typing import Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from server.config import env_settings


def search_cases(query: str, category: str) -> str:
    url = f"{env_settings.MARTECH_KB_ENDPOINT}/qa"
    headers = {
        "Authorization": f"Bearer {env_settings.MARTECH_KB_TOKEN}",
    }

    input_data = {
        "question": query,
        "index_name": category,
        "top_k": 8,
        "search_only": True,
    }

    resp = requests.post(
        headers=headers,
        data=json.dumps(input_data, ensure_ascii=False).encode("utf-8"),
        url=url,
    )

    resp = resp.json()

    res = ""

    if "sources" in resp:
        for idx, source in enumerate(resp["sources"]):
            res += f"case #{idx + 1}\n"
            for k, v in source.items():
                res += f"{k}: {v}\n"

    return res


class CaseSearchInput(BaseModel):
    query: str = Field(..., description="search query to look up")


class BeautiCareCaseSearchTool(BaseTool):
    """Tool that you can search marketing and ads creative cases for beauti care industry."""

    name: str = "beauti_care_case_search"
    chinese_name: str = "美妆个护案例库"

    description: str = """美妆和个人护理行业的广告创意案例的查询工具，
    其中也包含了每个案例的受众人群、广告主、产品卖点等相关信息。"""
    args_schema: Type[BaseModel] = CaseSearchInput

    def _run(self, query: str):
        return search_cases(query, "beauti_care_processed_glm")


class MaternalToyCaseSearchTool(BaseTool):
    name: str = "maternal_toy_case_search"
    chinese_name: str = "母婴玩具案例库"

    description: str = """母婴和玩具行业的广告创意案例的查询工具，
    其中也包含了每个案例的受众人群、广告主、产品卖点等相关信息。"""

    args_schema: Type[BaseModel] = CaseSearchInput

    def _run(self, query: str):
        return search_cases(query, "toys_processed_glm")
