from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Extra


class BaseSearcher(ABC, BaseModel):
    name: str

    class config:
        extra = Extra.forbid

    @abstractmethod
    def run(self, query: str) -> str:
        pass
