import json

import requests
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from loguru import logger

from server.config import env_settings


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.info(self.text)


KB_ENDPOINT = "http://127.0.0.1:7861/qa"
INDEX_NAME = "wine_materials_v2"
HEADERS = {
    "Authorization": "Bearer 007",
}


llm = ChatOpenAI(
    api_key=env_settings.OPENAI_API_KEY,
    model_name="gpt-3.5-turbo-1106",
    streaming=True,
)


def generate_research_summary(topic: str, content: str, callbacks=None):
    tmpl = """你是行业调研专家,下面提供了一个话题和相关资料，请根据提供的资料围绕这个话题，
    写500字左右的总结，如果提供的资料中没有找到合适的信息，用你的最佳判断进行总结。

    【写作要求】
    根据话题和资料，找到一些论点，围绕论点进行论证，论证过程尽量使用资料中的统计数据客观呈现。
    文字中不要有“根据提供的材料”或者类似的文字。
    
    【话题】
    {topic}
    

    【相关资料】
    {content}
    """
    prompt = PromptTemplate(input_variables=["topic", "content"], template=tmpl)
    chain = LLMChain(prompt=prompt, llm=llm)
    inp = {"topic": topic, "content": content}
    res = chain(inp, callbacks=callbacks)["text"]
    logger.info(f"getting research summary for query: {res}")
    return res


def search_kb(query: str, top_k: int = 8):
    input_data = {
        "question": query,
        "index_name": INDEX_NAME,
        "top_k": top_k,
        "search_only": True,
    }
    content = ""
    try:
        resp = requests.post(
            headers=HEADERS,
            data=json.dumps(input_data, ensure_ascii=False).encode("utf-8"),
            url=KB_ENDPOINT,
        )
        resp.raise_for_status()
        resp = resp.json()
        for source in resp["sources"]:
            content += source["content"] + "\n\n"
        logger.info(f"getting content: {content}")

    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
    return content


def topic_research_page():
    with st.form("### 葡萄酒行研助手"):
        topic = st.text_input(
            "输入一个您希望研究的话题",
            placeholder="e.g. 中国进口葡萄酒市场的情况和趋势2022年-2023年",
        )

        submit_btn = st.form_submit_button(
            "Go!",
            use_container_width=True,
            disabled=False,
        )

    if submit_btn:
        answer = st.empty()
        stream_handler = StreamHandler(
            answer,
            initial_text="`开始思考:`\n\n",
        )
        content = search_kb(topic)
        result = generate_research_summary(
            topic=topic,
            content=content,
            callbacks=[stream_handler],
        )
        answer.info(result)
        with st.expander("参考案例", expanded=False):
            st.write(content)


if __name__ == "__main__":
    topic_research_page()
