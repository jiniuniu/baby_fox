from langchain.llms.base import BaseLLM

from baby_fox.experimental.tools.google_search import GoogleSearch

LLM_TOOL_CLS = [GoogleSearch]


def load_llm_tools(llm: BaseLLM):
    tools = []
    for cls in LLM_TOOL_CLS:
        tools.append(cls(llm=llm).as_tool())
    return tools


def load_tools():
    pass
