import textwrap
import time

from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.llms import OpenAIChat
from langchain.prompts import PromptTemplate

from baby_fox.llms.chatglm_api import ChatGLMApi

PROMPT_SELECT_TEMPL = """
针对输入到语言模型的原始文本，选择最适合该输入的模型提示。您将得到可用提示
的名称以及最适合该提示的描述。如果您认为修改原始输入将最终导致语言模型产生
更好的回答，则可以对其进行修改。

<< 格式 >>

返回一个Markdown代码片段，其中包含一个 JSON 对象的代码，格式如下：
```json
{{{{
    "destination": string \\ 提示的名称或者 "DEFAULT"
    "next_inputs": string \\ 原始的输入或者它可能的修改版本
}}}}
```

请注意: "destination" 必须是下面指定的候选提示名称之一，或者如果输入
不适合任何候选提示，则可以为 "DEFAULT"。请记住："next_inputs" 如果您
认为不需要进行任何修改，可以直接使用原始输入。

<< 候选提示 >>
{candidates}

<< 输入 >>
{{input}}

<< 输出 >>
"""


PHYSICS_TEMPL = """
你是一位非常聪明的物理教授。你善于用简明易懂的方式回答物理问题。当你不知道某个
问题的答案时，你会坦率承认自己不知道。

问题：
{input}
"""

MATH_TEMPL = """
你是一位非常优秀的数学家。你擅长回答数学问题。
你之所以能够做得这么好，是因为你能够将难题分解成组成部分，回答每个组成部分，
然后将它们组合起来回答更广泛的问题。

问题：
{input}
"""

prompts_info = [
    {"name": "physics", "description": "擅长回答物理问题", "prompt_template": PHYSICS_TEMPL},
    {"name": "math", "description": "擅长回答数学问题", "prompt_template": MATH_TEMPL},
]


llm = OpenAIChat(temperature=0.0)
candidate_chains = {}
for p_info in prompts_info:
    name = p_info["name"]
    prompt_template = p_info["prompt_template"]
    prompt = PromptTemplate(template=prompt_template, input_variables=["input"])
    chain = LLMChain(llm=llm, prompt=prompt)
    candidate_chains[name] = chain
default_chain = ConversationChain(llm=llm, output_key="text")


# 构建提示选择的提示
candiates_str = "\n".join([f"{p['name']}: {p['description']}" for p in prompts_info])
prompt_select_template = PROMPT_SELECT_TEMPL.format(candidates=candiates_str)

# 解析输出结果
prompt = PromptTemplate(
    template=prompt_select_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)

router_chain = LLMRouterChain.from_llm(llm, prompt)

chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=candidate_chains,
    default_chain=default_chain,
    verbose=True,
)


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


while True:
    try:
        user_input = input("请输入您的问题：")
        response = chain.run(user_input)
        output_response(response)
    except KeyboardInterrupt:
        break
