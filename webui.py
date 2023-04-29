import streamlit as st
from streamlit_chat import message

from baby_fox.chat_bot import ChatBot

chat_bot = ChatBot()

st.set_page_config(page_title="Baby fox", page_icon=":robot:")


def predict(input, history=None):
    if history is None:
        history = []

    with container:
        if len(history) > 0:
            for i, (query, response) in enumerate(history):
                message(query, avatar_style="big-smile", key=str(i) + "_user")
                message(response, avatar_style="bottts", key=str(i))

        message(input, avatar_style="big-smile", key=str(len(history)) + "_user")
        st.write("AI正在回复:")
        with st.empty():
            response, history = chat_bot.answer(input, history)
            st.write(response)

    return history


container = st.container()

# create a prompt text for the text generation
prompt_text = st.text_area(label="用户命令输入", height=100, placeholder="请在这儿输入您的命令")

if "state" not in st.session_state:
    st.session_state["state"] = []

if st.button("发送", key="predict"):
    with st.spinner("AI正在思考，请稍等........"):
        # text generation
        st.session_state["state"] = predict(prompt_text, st.session_state["state"])
