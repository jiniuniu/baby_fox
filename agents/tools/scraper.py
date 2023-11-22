from typing import Type

from bs4 import BeautifulSoup
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import SeleniumURLLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from server.config import env_settings


def scrape_content(url, question):
    urls = [url]
    loader = SeleniumURLLoader(urls)
    docs = loader.load()

    if docs is not None and len(docs) > 0:
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        soup = BeautifulSoup(docs_transformed[0].page_content, "html.parser")
        # title = soup.find_all("div", attrs={"class": "project_title"})[0].text.strip()
        # content = soup.find_all("div", attrs={"id": "article_con"})[0].text
        # text = f"标题：{title}\n\n内容：\n{content}"
        text = soup.get_text()
        if len(text) > 1000:
            summary = summarise_content(text, question)
            return summary
        else:
            return text
    return ""


def summarise_content(content, ques):
    llm = ChatOpenAI(temperature=0, api_key=env_settings.OPENAI_API_KEY)
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


class ScraperInput(BaseModel):
    """Inputs for scrape_content function"""

    url: str = Field(description="The url or link of the website to be scraped")
    question: str = Field(
        description="The question or the query that users give to the agent"
    )


class BabyFoxScraperTool(BaseTool):
    name: str = "website_scraper_tool"
    chinese_name: str = "内置爬虫"
    description = "useful when you need to get data from a website url, passing both url and question to the function; DO NOT make up any url, the url should only be from the search results"
    args_schema: Type[BaseModel] = ScraperInput

    def _run(self, url: str, question: str):
        return scrape_content(url, question)

    def _arun(self, url: str):
        raise NotImplementedError("error here")


if __name__ == "__main__":
    url = "https://creative.adquan.com/show/337681"
    question = "对进行总结"
    tool = BabyFoxScraperTool()
    res = tool.run({"url": url, "question": question})
    print(res)
