import textwrap
import time

from langchain.llms import OpenAI

from baby_fox.experimental.chains.search_chain import SearchChain
from baby_fox.llms.chatglm_api import ChatGLMApi


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
    print("----------------------------------------------------------------")


if __name__ == "__main__":
    # llm = ChatGLMApi()
    llm = OpenAI(temperature=0.0, model_name="gpt-3.5-turbo", max_tokens=2048)
    search_chain = SearchChain(llm=llm, verbose=True)
    while True:
        try:
            user_input = input("请输入您的问题：")
            response = search_chain({"query": user_input})["output"]
            output_response(response)
        except KeyboardInterrupt:
            break
