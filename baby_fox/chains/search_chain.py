import json
import logging
import threading
from typing import Dict, List

from langchain import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.utilities.google_search import GoogleSearchAPIWrapper

from baby_fox.chains.prompt import CONTEXT_BASED_ANSWER_TEMPL, QUERY_EXPANSION_TEMPL

logging.basicConfig(level=logging.INFO)


class SearchChain(Chain):
    """Chain that takes input query and output search results."""

    llm: BaseLanguageModel
    searcher: GoogleSearchAPIWrapper = GoogleSearchAPIWrapper()
    input_key: str = "query"
    output_key: str = "output"
    max_context_length: int = 2000
    max_num_queries: int = 3

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
        logging.info(f"Query expansion prompt: \n{query_expansion_prompt}")
        res_str = self.llm(query_expansion_prompt)

        try:
            res = json.loads(res_str)
            related_queries = res["related_queries"]
            logging.info(f"Got related queries: {related_queries}")
        except ValueError:
            logging.info(f"Could not parse llm output: {res_str}")
            related_queries = []

        queries = [query] + related_queries
        queries = queries[: self.max_num_queries]
        search_res_dict = self._search(queries)
        context = self._format_search_results(search_res_dict)
        qa_with_context_prompt = PromptTemplate(
            input_variables=["query", "context"], template=CONTEXT_BASED_ANSWER_TEMPL
        )
        qa_with_context_prompt = qa_with_context_prompt.format(
            query=query, context=context
        )
        logging.info(f"QA with context: {qa_with_context_prompt}")
        res = self.llm(qa_with_context_prompt)
        return {self.output_key: res}

    def _format_search_results(self, search_res: Dict[str, str]) -> str:
        res = ""
        for q, ans in search_res.items():
            res += q + "\n" + ans + "\n"
        logging.info("Got full search results: %s", res)
        res = res[: self.max_context_length]
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
