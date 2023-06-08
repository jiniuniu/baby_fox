import textwrap
import time

from langchain.chat_models import ChatOpenAI

from baby_fox.experimental.agents.chat_agent import build_chat_agent_executor
from baby_fox.experimental.tools import load_llm_tools


def output_response(response: str) -> None:
    if not response:
        exit(0)
    for line in textwrap.wrap(response, width=60):
        for word in line.split():
            for char in word:
                print(char, end="", flush=True)
                time.sleep(0.1)  # Add a delay of 0.1 seconds between each character
            print(" ", end="", flush=True)  # Add a space between each word
        print()  # Move to the next line after each line is printed
    print("-" * 60)


if __name__ == "__main__":
    llm = ChatOpenAI(temperature=0.0)
    tools = load_llm_tools(llm)
    agent_executor = build_chat_agent_executor(llm, tools, verbose=True)
    while True:
        try:
            user_input = input("请输入您的问题：")
            response = agent_executor.run(user_input)
            output_response(response)
        except KeyboardInterrupt:
            break
