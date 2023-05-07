import json
import logging
import threading
from typing import Dict, List

from langchain import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.utilities.google_search import GoogleSearchAPIWrapper

from baby_fox.chains.prompt import (
    CONTEXT_BASED_ANSWER_TEMPL,
    PARAGRPAPH_TEMPL,
    QUERY_EXPANSION_TEMPL,
)

logging.basicConfig(level=logging.INFO)


class SearchChain(Chain):
    """Chain that takes input query and output search results."""

    llm: BaseLanguageModel
    searcher: GoogleSearchAPIWrapper = GoogleSearchAPIWrapper()
    input_key: str = "query"
    output_key: str = "output"
    max_context_length: int = 2000

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

        # 与llm交互得到相关问题延展
        query_expansion_prompt = PromptTemplate(
            input_variables=["query"], template=QUERY_EXPANSION_TEMPL
        )
        query_expansion_prompt = query_expansion_prompt.format(query=query)
        logging.info(f"Query expansion prompt: \n{query_expansion_prompt}")
        res_str = self.llm(query_expansion_prompt)
        try:
            res = json.loads(res_str)
            queries = res["related_queries"]
            logging.info(f"Got related queries: {queries}")
        except ValueError:
            logging.info(f"Could not parse llm output: {res_str}")
            queries = [query]
        search_res_dict = self._search(queries)

        # 对每个延展问题，搜索资料并通过llm总结整理
        summary_dict = {}
        for q, context in search_res_dict.items():
            context = context[: self.max_context_length]
            qa_with_context_prompt = PromptTemplate(
                input_variables=["query", "context"],
                template=CONTEXT_BASED_ANSWER_TEMPL,
            )
            qa_with_context_prompt = qa_with_context_prompt.format(
                query=q, context=context
            )
            logging.info(f"QA with context: {qa_with_context_prompt}")
            summary = self.llm(qa_with_context_prompt)
            summary_dict[q] = summary

        # 把每个延展问题的总结作为资料给到llm写成一篇文章
        cnt = 1
        materials = ""
        outlines = ""
        for outline, material in summary_dict.items():
            materials += f"{cnt}. {material}\n"
            outlines += f"{cnt}. {outline}\n"
            cnt += 1
        paragraph_prompt = PromptTemplate(
            input_variables=["outlines", "materials"], template=PARAGRPAPH_TEMPL
        )
        paragraph_prompt = paragraph_prompt.format(
            outlines=outlines, materials=materials
        )
        logging.info(f"article prompt: {paragraph_prompt}")
        res = self.llm(paragraph_prompt)

        return {self.output_key: res}

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
