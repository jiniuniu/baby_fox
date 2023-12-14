import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_option_menu import option_menu
from yaml.loader import SafeLoader

from agents.agent_builder.agent_chat_page import agent_chat_page
from agents.agent_builder.agent_management_page import agent_store_page

# from agents.agent_builder.agent_stream_chat_page import agent_stream_chat_page
from agents.agent_builder.image_desc_page import image_description_page


def home_page():
    pages = {
        "agent store": {
            "icon": "hdd-stack",
            "func": agent_store_page,
        },
        "agent chat": {
            "icon": "robot",
            "func": agent_chat_page,
        },
        "图生文": {
            "icon": "chat",
            "func": image_description_page,
        },
    }
    with st.sidebar:
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            None,
            options=options,
            icons=icons,
            default_index=default_index,
            menu_icon="cast",
        )

    if selected_page in pages:
        pages[selected_page]["func"]()


def initialize_session_state():
    if "name" not in st.session_state:
        st.session_state["name"] = None
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None


def login_page(credential_yaml: str):
    initialize_session_state()

    with open(credential_yaml) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )
    name, authentication_status, username = authenticator.login("Login", "main")

    if st.session_state["authentication_status"]:
        authenticator.logout("Logout", "sidebar")
        home_page()
    elif st.session_state["authentication_status"] is False:
        st.error("用户名/密码输入不正确")
    elif st.session_state["authentication_status"] is None:
        st.warning("请输入用户名和密码")


if __name__ == "__main__":
    cred_yml = "./agents/agent_builder/credentials.yaml"
    login_page(cred_yml)
