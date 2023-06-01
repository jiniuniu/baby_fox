from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.memory import ConversationBufferWindowMemory

CHAT_PROMPT_TMPL = """
这是用户和AI的聊天历史
{chat_history}
用户: {human_input}
AI:
"""


class ChatBot:
    def __init__(self, llm: BaseLanguageModel, history_len: int = 10) -> None:
        self.llm = llm

        self.chat_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["chat_history", "human_input"],
                template=CHAT_PROMPT_TMPL,
            ),
            memory=ConversationBufferWindowMemory(
                memory_key="chat_history",
                ai_prefix="AI",
                human_prefix="用户",
                k=history_len,
            ),
        )

    def answer_directly(self, query: str, chat_history_included=True) -> str:
        if chat_history_included:
            res = self.chat_chain.predict(human_input=query)
        else:
            res = self.llm(query)
        return res
