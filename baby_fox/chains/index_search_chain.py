from typing import Dict, List

from langchain import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.vectorstores import FAISS

from baby_fox.chains.prompt import CONTEXT_BASED_ANSWER_TEMPL


class IndexSearchChain(Chain):
    top_k: int = 5
    llm: BaseLanguageModel
    index: FAISS

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
        query = inputs["query"]
        related_docs = self.index.similarity_search_with_score(query, k=self.top_k)
        context = "\n".join([doc.page_content for doc, _ in related_docs])
        qa_with_context_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=CONTEXT_BASED_ANSWER_TEMPL,
        )
        qa_with_context_prompt = qa_with_context_prompt.format(
            query=query, context=context
        )
        res = self.llm(qa_with_context_prompt)
        return {self.output_key: res}
