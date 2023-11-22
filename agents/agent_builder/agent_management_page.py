import json
from datetime import datetime

import streamlit as st

from agents.agent_builder.utils import db_to_df, display_table
from agents.agent_loader import AgentConfig
from agents.db.repository import add_or_update_to_db, delete_from_db, exists_in_db
from agents.tools import TOOL_MAP

ALL_TOOL_NAMES = [key for key in TOOL_MAP.keys()]


def init_this_page():
    if "key" not in st.session_state:
        st.session_state["key"] = ""
    if "agent_config" not in st.session_state:
        st.session_state["agent_config"] = AgentConfig(
            name="",
            description="",
            instructions="",
            tools=[],
        )


def agent_store_page():
    init_this_page()
    df = db_to_df()
    st.write("## 小助理配置")
    with st.sidebar:
        selection = display_table(df)
    key = ""

    if selection:
        agent_config_str = selection[0]["agent_config"]
        agent_config = AgentConfig.model_validate_json(agent_config_str)
        st.session_state["agent_config"] = agent_config
        st.session_state["key"] = str(selection[0]["agent_key"])
        key = st.session_state["key"]

    with st.expander("新建"):
        new_key = st.text_input("新增序号", placeholder="123")
        if st.button(
            "提交",
            disabled=(len(new_key) == 0),
            on_click=create_new_config,
            args=[new_key],
            use_container_width=True,
        ):
            st.toast("new record added!")
            st.experimental_rerun()

    st.write(f"## 当前助理编号: {key}")

    btn_cols = st.columns(3)

    update_agent_config()

    btn_cols[0].button(
        "保存配置",
        on_click=save_config,
        args=[st.session_state["key"]],
        use_container_width=True,
        disabled=(len(selection) == 0),
    )

    btn_cols[1].button(
        "删除",
        on_click=delete_from_db,
        args=[st.session_state["key"]],
        use_container_width=True,
        disabled=(len(selection) == 0),
    )

    now = datetime.now()
    btn_cols[2].download_button(
        "下载",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"agent_config_{now:%Y%m%d%H%M}.csv",
        key="download_btn",
        use_container_width=True,
        disabled=(len(selection) != 0),
    )


def create_new_config(key: str):
    if exists_in_db(key):
        st.warning(f"序号：{key} 已经存在了")
        return
    agent_config: AgentConfig = st.session_state["agent_config"]
    agent_config_json = agent_config.model_dump(mode="json")
    agent_config_json_str = json.dumps(
        agent_config_json,
        ensure_ascii=False,
    )
    add_or_update_to_db(
        key=key,
        agent_config=agent_config_json_str,
    )


def save_config(key: str):
    agent_config: AgentConfig = st.session_state["agent_config"]
    agent_config_json = agent_config.model_dump(mode="json")
    agent_config_json_str = json.dumps(
        agent_config_json,
        ensure_ascii=False,
    )
    add_or_update_to_db(
        key=key,
        agent_config=agent_config_json_str,
    )


def update_agent_config():
    agent_config: AgentConfig = st.session_state["agent_config"]
    name = st.text_input(
        "## 名称",
        value=agent_config.name,
    )
    description = st.text_area(
        "## 描述",
        value=agent_config.description,
    )
    instructions = st.text_area(
        "## 系统提示",
        value=agent_config.instructions,
        height=400,
    )
    tool_names = [
        tool_name
        for tool_name in agent_config.tool_names
        if tool_name in ALL_TOOL_NAMES
    ]

    model = st.selectbox("## 模型选择", ["gpt-4-1106-preview", "gpt-3.5-turbo-1106"])

    selected_tool_names = st.multiselect(
        "## 配置工具（可多选）",
        ALL_TOOL_NAMES,
        tool_names,
    )
    agent_config.name = name
    agent_config.description = description
    agent_config.instructions = instructions
    agent_config.tool_names = selected_tool_names
    agent_config.model = model


if __name__ == "__main__":
    agent_store_page()
