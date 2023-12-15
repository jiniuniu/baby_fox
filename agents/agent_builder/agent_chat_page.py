import json

import requests
import streamlit as st
from loguru import logger

from server.config import env_settings

AGENT_URL = "http://127.0.0.1:7862"
CHAT_ENDPOINT = "/agent_stream_chat"
LIST_ENDPOINT = "/list_agents"
TOKEN = env_settings.KNOWN_ACCESS_TOKEN
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}


def get_agents_infos():
    key_and_names = []
    try:
        with requests.get(
            headers=HEADERS,
            url=f"{AGENT_URL}{LIST_ENDPOINT}",
        ) as resp:
            resp.raise_for_status()
            res = resp.json()

        agents_infos = res["agents_infos"]
        for agent_info in agents_infos:
            key_and_names.append(agent_info["key"] + ":" + agent_info["name"])
        return key_and_names

    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")


def process_response(prompt: str, selected_agent_key: str):
    chat_history = st.session_state["chat_history"]
    input_data = {
        "user_message": prompt,
        "agent_key": selected_agent_key,
        "chat_history": chat_history,
    }
    res = ""
    container = st.container().empty()
    try:
        with requests.post(
            headers=HEADERS,
            data=json.dumps(
                input_data,
                ensure_ascii=False,
            ).encode("utf-8"),
            url=f"{AGENT_URL}{CHAT_ENDPOINT}",
            stream=True,
        ) as response:
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=1024):
                if not chunk:
                    break
                try:
                    chunk = chunk.decode("'utf-8'")
                    res += chunk
                    container.markdown(res + " |")
                except UnicodeDecodeError:
                    st.info("Unicode decode error!")
            container.markdown(res)
        return res

    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")


def setup_this_page():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []


def clear_msgs():
    if "chat_history" in st.session_state:
        st.session_state["chat_history"] = []


def display_msgs():
    if "chat_history" in st.session_state:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])


def agent_chat_page():
    setup_this_page()

    with st.sidebar:
        key_and_names = get_agents_infos()
        selected_agent = st.selectbox("Choose your agent", key_and_names)
        clear_btn = st.button("clear chat history", use_container_width=True)
        if clear_btn:
            clear_msgs()
    display_msgs()
    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            # response = process_large_response(prompt, selected_agent_key)
            selected_agent_key = selected_agent.split(":")[0]
            resp = process_response(
                prompt=prompt, selected_agent_key=selected_agent_key
            )
            agent_message = resp
            # thought_steps = response["thought_steps"]
            # with st.expander("思考过程"):
            #     st.write(thought_steps)
            # st.write(agent_message)

        st.session_state["chat_history"].append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        st.session_state["chat_history"].append(
            {
                "role": "assistant",
                "content": agent_message,
            }
        )


if __name__ == "__main__":
    agent_chat_page()
