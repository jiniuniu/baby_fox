from typing import List, Tuple

from checksumdir import dirhash
from langchain.base_language import BaseLanguageModel
from langchain.chains import ConversationalRetrievalChain, ConversationChain
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import OpenAIChat
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import FAISS

from baby_fox.config import *
from baby_fox.logger import get_logger
from baby_fox.prompts import (
    CHAT_PROMPT,
    CONDENSE_QUESTION_PROMPT,
    QA_WITH_CONTEXT_PROMPT,
)

log = get_logger(__name__)


class ChatBot:
    llm: BaseLanguageModel = OpenAIChat(
        temperature=0.0, model_name="gpt-3.5-turbo", max_tokens=2048
    )
    history_len: int = 5
    last_index_path = os.path.join(INDEX_ROOT, DEFAULT_KNOWLEDGE_NAME)
    last_index_checksum = dirhash(last_index_path)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_PATH, model_kwargs={"device": "cpu"}
    )
    index: FAISS = FAISS.load_local(last_index_path, embeddings)

    # 两个对话历史库
    local_knowledge_chat_memory = []
    chat_memory: ConversationBufferWindowMemory = ConversationBufferWindowMemory(
        k=history_len
    )

    # 基于本地知识库聊天
    local_knowledge_chat_chain: ConversationalRetrievalChain = (
        ConversationalRetrievalChain.from_llm(
            llm,
            index.as_retriever(),
            return_source_documents=True,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            combine_docs_chain_kwargs={"prompt": QA_WITH_CONTEXT_PROMPT},
        )
    )

    # 基于LLM自有知识库聊天
    chat_chain: ConversationChain = ConversationChain(
        llm=llm, memory=chat_memory, prompt=CHAT_PROMPT
    )

    def answer_directly(self, query: str, chat_history_included=True) -> str:
        if chat_history_included:
            res = self.chat_chain({"input": query})["response"]
        else:
            res = self.llm(query)
        return res

    def answer_with_local_sources(
        self, query: str, index_path: str, chat_history_included=True
    ) -> Tuple[str, List[str]]:
        # 消除对话历史
        if not chat_history_included:
            self.local_knowledge_chat_memory = []

        # 知识库更新，需要重新加载并清楚对话历史
        reloaded = self._reload_index_if_needed(index_path)
        if reloaded:
            self.local_knowledge_chat_chain.retriever = self.index.as_retriever()
            self.local_knowledge_chat_memory = []

        result = self.local_knowledge_chat_chain(
            {"question": query, "chat_history": self.local_knowledge_chat_memory}
        )
        answer = result["answer"]
        related_docs = result["source_documents"]

        self.local_knowledge_chat_memory.append((query, answer))
        self.local_knowledge_chat_memory = self.local_knowledge_chat_memory[
            -self.history_len :
        ]

        sources = [doc.page_content for doc in related_docs]
        return answer, sources

    def _reload_index_if_needed(self, index_path: str) -> bool:
        # 检查索引是否存在以及是否更新
        index_checksum = dirhash(index_path)
        if (index_path == self.last_index_path) and (
            self.last_index_checksum == index_checksum
        ):
            return False
        self.index = FAISS.load_local(index_path, self.embeddings)
        self.last_index_path = index_path
        self.last_index_checksum = index_checksum
        return True
