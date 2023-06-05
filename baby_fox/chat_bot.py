from typing import List, Tuple

from checksumdir import dirhash
from langchain.base_language import BaseLanguageModel
from langchain.chains import ConversationalRetrievalChain, ConversationChain
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import Document
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
    """用来调度各种api的任务"""

    # 对话保留的回合数
    history_len: int = 5

    # 两个用来存储对话历史对象（直接的对话和基于知识库的对话）
    local_knowledge_chat_memory = []
    chat_memory: ConversationBufferWindowMemory = ConversationBufferWindowMemory(
        k=history_len
    )

    def __init__(self, llm: BaseLanguageModel) -> None:
        self.llm = llm

        # 初始化需要加载的索引工具
        self.last_index_path = os.path.join(INDEX_ROOT, DEFAULT_KNOWLEDGE_NAME)
        self.last_index_checksum = dirhash(self.last_index_path)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_PATH, model_kwargs={"device": "cpu"}
        )
        self.index: FAISS = FAISS.load_local(self.last_index_path, self.embeddings)

        # 本地知识库 + LLM的聊天
        self.local_knowledge_chat_chain: ConversationalRetrievalChain = (
            ConversationalRetrievalChain.from_llm(
                self.llm,
                self.index.as_retriever(),
                return_source_documents=True,
                condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                combine_docs_chain_kwargs={"prompt": QA_WITH_CONTEXT_PROMPT},
            )
        )

        # 纯LLM聊天
        self.chat_chain: ConversationChain = ConversationChain(
            llm=llm, memory=self.chat_memory, prompt=CHAT_PROMPT
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
        related_docs: List[Document] = result["source_documents"]

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
