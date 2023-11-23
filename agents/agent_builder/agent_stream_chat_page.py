import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler

from agents.agent_loader import AgentLoader
from agents.db.repository import list_all_keys
from server.schemas import Message, Role
from server.utils import process_chat_history


def chat(user_message: str, agent_key: str):
    st_cb = StreamlitCallbackHandler(st.container())
    agent = AgentLoader.load_agent(agent_key)
    agent.memory.chat_memory = process_chat_history(st.session_state["chat_history"])
    inp = {"input": user_message}
    response = agent(inp, callbacks=[st_cb])
    return response


def setup_this_page():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []


def clear_msgs():
    if "chat_history" in st.session_state:
        st.session_state["chat_history"] = []


def display_msgs():
    if "chat_history" in st.session_state:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg.role):
                st.write(msg.content)


def agent_stream_chat_page():
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
            response = chat(prompt, selected_agent_key)
            agent_message = response["output"]
            thought_steps = response["intermediate_steps"]
            with st.expander("思考过程"):
                st.write(thought_steps)
            st.write(agent_message)

        st.session_state["chat_history"].append(
            Message(
                role=Role.USER,
                content=prompt,
            )
        )
        st.session_state["chat_history"].append(
            Message(
                role=Role.ASSISTANT,
                content=agent_message,
            )
        )
