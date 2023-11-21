import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory.chat_message_histories import ChatMessageHistory

from agents.agent_loader import AgentLoader
from agents.db.repository import list_all_keys

AVATARS = {"human": "user", "ai": "assistant"}


def setup_this_page():
    if "msgs" not in st.session_state:
        st.session_state["msgs"] = ChatMessageHistory()

    if "steps" not in st.session_state:
        st.session_state["steps"] = {}


def clear_msgs():
    if "msgs" in st.session_state:
        msgs: ChatMessageHistory = st.session_state["msgs"]
        msgs.clear()
        msgs.add_ai_message("How can I help you?")
        st.session_state.steps = {}


def display_msgs():
    if "msgs" in st.session_state:
        msgs: ChatMessageHistory = st.session_state["msgs"]
        for idx, msg in enumerate(msgs.messages):
            with st.chat_message(AVATARS[msg.type]):
                for step in st.session_state.steps.get(str(idx), []):
                    if step[0].tool == "_Exception":
                        continue
                    with st.status(
                        f"**{step[0].tool}**: {step[0].tool_input}", state="complete"
                    ):
                        st.write(step[0].log)
                        st.write(step[1])
                st.write(msg.content)


def agent_chat_page():
    setup_this_page()
    display_msgs()
    with st.sidebar:
        all_agent_keys = list_all_keys()
        selected_agent_key = st.selectbox("Choose your agent", all_agent_keys)
        agent = AgentLoader.load_agent(selected_agent_key)
        clear_btn = st.button("clear chat history", use_container_width=True)
        if clear_btn:
            clear_msgs()

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            inp = {"input": prompt}
            response = agent(inp, callbacks=[st_callback])
            st.write(response["output"])
            st.session_state.steps[
                str(len(st.session_state["msgs"].messages) - 1)
            ] = response["intermediate_steps"]
