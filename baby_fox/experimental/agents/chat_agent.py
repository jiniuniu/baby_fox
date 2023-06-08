from typing import List

from langchain import LLMChain
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationBufferWindowMemory

PREFIX = """你在和一个human对话，按照给定的格式尽可能地回答以下问题。你可以使用下面这些工具："""
FORMAT_INSTRUCTIONS = """回答时需要遵循以下用---括起来的格式：

---
Question: 我需要回答的问题
Thought: 回答这个上述我需要做些什么
Action: 选择的工具名，必须是[{tool_names}]其中的一种
Action Input: 选择工具所需要的输入
Observation: 选择工具返回的结果
...（这个思考/行动/行动输入/观察可以重复N次）
Thought: 我现在知道最终答案
Final Answer: 原始输入问题的最终答案
---"""
SUFFIX = """开始!
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""


def build_chat_agent_executor(
    llm: BaseLLM, tools: List[Tool], verbose: bool = False
) -> AgentExecutor:
    prompt = ZeroShotAgent.create_prompt(
        tools=tools,
        prefix=PREFIX,
        suffix=SUFFIX,
        format_instructions=FORMAT_INSTRUCTIONS,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )
    memory = ConversationBufferWindowMemory(memory_key="chat_history")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=verbose)

    return AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, memory=memory, verbose=verbose
    )
