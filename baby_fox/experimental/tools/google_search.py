from langchain.chains import LLMChain, LLMRequestsChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

from baby_fox.experimental.tools.base import LLMBase


class GoogleSearch(LLMBase):
    @property
    def name(self) -> str:
        return "google_search"

    @property
    def description(self) -> str:
        """对工具的描述"""
        return "用户提问涉及当下或者近期的事件，可以用来进行 Google 搜索查询相关信息"

    template: str = """
    在 >>> 和 <<< 之间是来自原始搜索结果文本。
    请从中提取以下问题的回答，如果没有找到相关的信息，就说"not found"。
    问题：
    '{query}'

    使用这样的格式
    Extracted:<answer or "not found">
    >>>{requests_result}<<<
    Extracted:"""

    prompt = PromptTemplate(
        input_variables=["query", "requests_result"], template=template
    )

    url: str = "https://www.google.com/search?q="

    def __init__(self, llm: BaseLLM) -> None:
        llm_chain = LLMChain(llm=llm, prompt=self.prompt)
        self.chain = LLMRequestsChain(llm_chain=llm_chain)

    def run(self, question: str) -> str:
        inputs = {"query": question, "url": self.url + question.replace(" ", "+")}
        return self.chain(inputs)["output"]


if __name__ == "__main__":
    from langchain.llms import OpenAIChat

    llm = OpenAIChat(temperature=0.0)
    searcher = GoogleSearch(llm=llm)
    print(searcher.run("第一个登月的是谁？"))
