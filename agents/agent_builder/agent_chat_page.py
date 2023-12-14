import json

import requests
import streamlit as st
from loguru import logger

from agents.db.repository import list_all_keys
from server.config import env_settings

AGENT_CHAT_URL = "http://127.0.0.1:7862/agent_stream_chat"

TOKEN = env_settings.KNOWN_ACCESS_TOKEN


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}


def process_large_response(prompt: str, selected_agent_key: str):
    input_data = {
        "user_message": prompt,
        "agent_key": selected_agent_key,
        "chat_history": st.session_state["chat_history"],
    }
    try:
        with requests.post(
            headers=HEADERS,
            data=json.dumps(
                input_data,
                ensure_ascii=False,
            ).encode("utf-8"),
            url=AGENT_CHAT_URL,
            stream=True,
        ) as response:
            response.raise_for_status()

            buffer = bytearray()
            for chunk in response.iter_content(chunk_size=32):
                if chunk:
                    buffer.extend(chunk)

                    # Try to decode the buffer to a string
                    try:
                        data_str = buffer.decode("utf-8")
                        buffer.clear()

                        # Process your data here as needed
                        # ...

                    except UnicodeDecodeError:
                        # If there's a Unicode error, continue to the next chunk
                        # and append more bytes to the buffer
                        pass
            # Process any remaining data after the loop
            if buffer:
                data_str = buffer.decode("utf-8")
            json_data = json.loads(data_str)
            return json_data

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
            url=AGENT_CHAT_URL,
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
        all_agent_keys = list_all_keys()
        selected_agent_key = st.selectbox("Choose your agent", all_agent_keys)
        clear_btn = st.button("clear chat history", use_container_width=True)
        if clear_btn:
            clear_msgs()
    display_msgs()
    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            # response = process_large_response(prompt, selected_agent_key)
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
