from abc import ABC, abstractmethod

from langchain.agents import Tool
from langchain.llms.base import BaseLLM


class Base(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def run(self, question: str) -> str:
        pass

    def as_tool(self) -> Tool:
        return Tool(name=self.name, func=self.run, description=self.description)


class LLMBase(Base):
    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm
