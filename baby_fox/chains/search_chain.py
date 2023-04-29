import threading
from typing import Dict, List

from langchain import PromptTemplate
from langchain.chains.base import Chain
from langchain.llms.base import LLM

from baby_fox.chains.prompt import CONTEXT_BASED_ANSWER_TEMPL, QUERY_EXPANSION_TEMPL
from baby_fox.search_tools.base import BaseSearcher


class SearchChain(Chain):
    """Chain that takes input query and output search results."""

    llm: LLM
    searcher: BaseSearcher
    input_key: str = "query"
    output_key: str = "output"

    @property
    def _chain_type(self) -> str:
        raise NotImplementedError

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        query = inputs[self.input_key]

        # query expansion to get more queries
        query_expansion_prompt = PromptTemplate(
            input_variables=["query"], template=QUERY_EXPANSION_TEMPL
        )
        query_expansion_prompt = query_expansion_prompt.format(query=query)
        related_queries_str = self.llm(query_expansion_prompt)
        related_queries = self._parse_str_to_list(related_queries_str)
        queries = [query] + related_queries
        # call search api to get earch query's search results
        search_res_dict = self._search(queries)
        context = self._format_search_results(search_res_dict)
        qa_with_context_prompt = PromptTemplate(
            input_variables=["query", "context"], template=CONTEXT_BASED_ANSWER_TEMPL
        )
        qa_with_context_prompt = qa_with_context_prompt.format(
            query=query, context=context
        )
        res = self.llm(qa_with_context_prompt)
        return {self.output_key: res}

    def _parse_str_to_list(self, queries_str: str) -> List[str]:
        res = eval(queries_str)
        if isinstance(res, List):
            return res
        else:
            return [res]

    def _format_search_results(self, search_res: Dict[str, str]) -> str:
        res = ""
        for q, ans in search_res.items():
            res += q
            res += ans
            res += "\n"
        return res

    def _search(self, queries: List[str]) -> Dict[str, str]:
        call_res = {}

        def _search_fn(query: str):
            res = self.searcher.run(query)
            call_res[query] = res
            return res

        all_threads = []
        for q in queries:
            t = threading.Thread(target=_search_fn, args=[q])
            all_threads.append(t)
        for t in all_threads:
            t.start()
        for t in all_threads:
            t.join()
        return call_res
