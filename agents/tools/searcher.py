from typing import Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.base import BaseTool
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(..., description="需要查询的搜索短语")
    # site: Optional[str] = Field(
    #     "",
    #     description="""if site is provided, the search result will be only from the provided site,
    #     the input should be the domain only, no http or https, example of the this parameter would
    #     be "digitaling.com"
    #     """,
    # )


class BabyFoxSearchTool(BaseTool):
    """Tool that queies DuckDuckGo search API"""

    name: str = "baby_fox_searcher"
    chinese_name: str = "免费通用搜索"
    description: str = """A wrapper around DuckDuckGo Search. 
    Useful for when you need to answer questions about current events. 
    Input should be 
        - required a search query
        - optionally, a site url, if provided, it means the search result will be only from the provided site.
    Output will be text string
    """
    api_wrapper: DuckDuckGoSearchAPIWrapper = DuckDuckGoSearchAPIWrapper(
        region="cn-zh",
        max_results=8,
        time="m",
    )

    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        # if site != "":
        #     if site.startswith("http://"):
        #         domain = site.replace("http://", "").split("/")[0]
        #     elif site.startswith("https://"):
        #         domain = site.replace("https://", "").split("/")[0]
        #     else:
        #         domain = site.split("/")[0]
        #     query += f" site:{domain}"

        return self.api_wrapper.run(query)
