import json

import requests
import streamlit as st
from loguru import logger

from agents.db.repository import list_all_keys
from server.config import env_settings

AGENT_CHAT_URL = "http://127.0.0.1:7862/agent_chat"

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

            # Buffer for partial content
            buffer = ""
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    buffer += chunk.decode("utf-8")

                    # Process buffer here if possible
                    # If your data allows for processing in parts,
                    # you can process and clear the buffer here

            # Final processing for any remaining data in the buffer
            json_data = json.loads(buffer)
            return json_data

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
            response = process_large_response(prompt, selected_agent_key)
            agent_message = response["agent_message"]
            thought_steps = response["thought_steps"]
            with st.expander("思考过程"):
                st.write(thought_steps)
            st.write(agent_message)

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
