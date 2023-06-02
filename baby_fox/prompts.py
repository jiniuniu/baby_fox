from langchain.prompts.prompt import PromptTemplate

CHAT_TMPL = """
以下是Human和AI之间友好的对话。
这个AI很健谈，并提供了很多来自其上下文的具体细节。如果这个AI不知道问题的答案，它会真诚地说出不知道。
当前的对话:
{history}
Human: {input}
AI:
"""
CHAT_PROMPT = PromptTemplate(input_variables=["history", "input"], template=CHAT_TMPL)


CONDENSE_QUESTION_PROMPT_TMPL = """
给定以下对话和跟进问题，请重新表述跟进问题以成为一个独立问题。
对话：
{chat_history}
跟进问题输入：{question}
独立问题：
"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(CONDENSE_QUESTION_PROMPT_TMPL)


QA_PROMPT_WITH_CONTEXT_TMPL = """使用以下上下文片段来回答问题。如果你不知道答案，就说你不知道，不要试图编造答案
{context}
问题: {question}
答案:"""
QA_WITH_CONTEXT_PROMPT = PromptTemplate(
    template=QA_PROMPT_WITH_CONTEXT_TMPL, input_variables=["context", "question"]
)
