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
            input_data = {
                "user_message": prompt,
                "agent_key": selected_agent_key,
                "chat_history": st.session_state["chat_history"],
            }
            try:
                resp = requests.post(
                    headers=HEADERS,
                    data=json.dumps(
                        input_data,
                        ensure_ascii=False,
                    ).encode("utf-8"),
                    url=AGENT_CHAT_URL,
                )
                resp.raise_for_status()
            except Exception as e:
                logger.error(f"error {e}")
                st.stop()

            response = resp.json()
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
