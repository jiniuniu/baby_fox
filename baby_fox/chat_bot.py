from typing import Any, List, Tuple

from baby_fox.chains.search_chain import SearchChain
from baby_fox.llms.chatglm import ChatGLM
from baby_fox.search_tools.google import GoogleSearcher


class ChatBot:
    def __init__(self):
        llm = ChatGLM()
        # have all the keys setup
        google_searcher = GoogleSearcher()
        self.search_chain = SearchChain(llm=llm, searcher=google_searcher)

    def answer(self, query: str, history=[]) -> Tuple[str, List[Any]]:
        self.search_chain.llm.history = history
        res = self.search_chain({"query": query})["output"]
        self.search_chain.llm.history[-1][0] = query
        return res, self.search_chain.llm.history
