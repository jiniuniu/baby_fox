import random
from typing import List, Type
from urllib.parse import quote

from bs4 import BeautifulSoup
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import AsyncHtmlLoader
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

from server.config import env_settings

DIGITALING_URL = "https://www.digitaling.com/search/projects?kw={}"


HOLIDAY_KEYWORDS = [
    "春节",
    "元宵节",
    "七夕",
    "端午节",
    "中秋节",
    "重阳节",
    "腊八",
    "情人节",
    "妇女节",
    "植树节",
    "愚人节",
    "清明节",
    "母亲节",
    "儿童节",
    "父亲节",
    "教师节",
    "国庆节",
    "程序员节",
    "感恩节",
    "圣诞节",
]


HOLIDAY_KEYWORDS_STR = ",".join(HOLIDAY_KEYWORDS)


def summarise_content(content, ques):
    llm = ChatOpenAI(
        api_key=env_settings.OPENAI_API_KEY,
        model="gpt-3.5-turbo-1106",
    )
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=3500, chunk_overlap=300
    )
    docs = text_splitter.create_documents([content])

    reduce_template_string = """I want you to act as a text summarizer to help me create a concise summary 
        of the text I provide. The summary can be up to 10 sentences in length, expressing the key points and 
        concepts written in the Chinese text without adding your interpretations. The summary should be focused on
        answering the given question and the other details which are not relevant to the given question can be ignored.
        My first request is to summarize this text – 
        {text}

        Question: {question}
        Answer:
    """
    reduce_template = PromptTemplate(
        template=reduce_template_string, input_variables=["text", "question"]
    )
    chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=reduce_template,
        combine_prompt=reduce_template,
        verbose=True,
    )
    return chain.run(input_documents=docs, question=ques)


def build_search_url(keyword: str):
    encoded_keyword = quote(keyword, safe="/:?=&")
    url = DIGITALING_URL.format(encoded_keyword)
    return url


def get_search_results(keyword: str, top_k: int = 3) -> List[str]:
    url = build_search_url(keyword)
    loader = AsyncHtmlLoader([url])
    docs = loader.load()
    if not docs or len(docs) == 0:
        return {}

    soup = BeautifulSoup(docs[0].page_content, "html.parser")

    results = process_search_results(soup)
    search_results = []
    for res in results:
        score = res.get("score") or 0
        if score < 8.0:
            continue
        url = res.get("url")
        search_results.append(url)
    random.shuffle(search_results)
    return search_results[:top_k]


def process_search_results(soup: BeautifulSoup) -> List[str]:
    elements = soup.find_all("div", attrs={"class": "works_bd"})
    res = []
    for element in elements:
        title_elem = element.find("h3", attrs={"class": "mg_b_10"})
        title = title_elem.a["title"]
        url = title_elem.a["href"]
        data = {
            "title": title,
            "url": url,
        }
        data_elem = element.find_all("em", attrs={"class": "v_m"})
        if len(data_elem) == 3:
            data["score"] = float(data_elem[0].get_text())
            data["num_bookmarks"] = int(data_elem[1].get_text())
            data["num_comments"] = int(data_elem[2].get_text())

        res.append(data)
    return res


def get_detail_page_contents(urls: List[str]) -> str:
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    res = ""
    for doc in docs:
        soup = BeautifulSoup(doc.page_content, "html.parser")
        title = soup.find("div", attrs={"class": "project_title"}).get_text().strip()
        content = soup.find("div", attrs={"class": "article_con"}).get_text()
        content = summarise_content(content, "请对这个广告创意的进行改写，尽量突出它的亮点")
        res += "--------------------------------\n"
        res += f"标题：{title}\n"
        res += f"内容：{content}\n"

    return res


class HolidayAdSearchInput(BaseModel):
    holiday_keyword: str = Field(
        ...,
        description=f"节日的名称，必须是{HOLIDAY_KEYWORDS_STR}其中的一个",
    )


class HolidayAdSearchTool(BaseTool):
    name: str = "holiday_ad_searcher"
    chinese_name: str = "节日案例库"
    description = "可以用来搜索节日相关的广告案例的一个工具，需要从用户问题中提取节日名称"
    args_schema: Type[BaseModel] = HolidayAdSearchInput

    def _run(self, holiday_keyword: str):
        urls = get_search_results(holiday_keyword)
        logger.info(f"getting urls: {urls}")
        res = get_detail_page_contents(urls)
        return res


if __name__ == "__main__":
    tool = HolidayAdSearchTool()
    res = tool.run({"holiday_keyword": "中秋节"})
    logger.info(res)
