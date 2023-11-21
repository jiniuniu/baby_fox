import json
from typing import Dict, Literal, Tuple

import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

from agents.db.data_model import AgentConfigModel
from agents.db.session import with_session


@with_session
def db_to_df(session) -> pd.DataFrame:
    records = session.query(AgentConfigModel).all()
    res = []
    for record in records:
        res.append(
            (
                record.key,
                record.agent_config,
            )
        )
    return pd.DataFrame(
        res,
        columns=[
            "agent_key",
            "agent_config",
        ],
    )


@with_session
def db_to_jsonl(session, output_path):
    records = session.query(AgentConfigModel).all()
    with open(output_path, "w") as f:
        for record in records:
            data = {}
            agent_config = json.loads(record.agent_config)
            data["agent_config"] = agent_config
            data["key"] = record.key
            line = json.dumps(data, ensure_ascii=False)
            f.write(line + "\n")
    return True


def config_aggrid(
    df: pd.DataFrame,
    columns: Dict[Tuple[str, str], Dict] = {},
    selection_mode: Literal["single", "multiple", "disabled"] = "single",
    use_checkbox: bool = True,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    # gb.configure_column("No", width=40)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    return gb


def display_table(df):
    gb = config_aggrid(df)

    doc_grid = AgGrid(
        df,
        gb.build(),
        columns_auto_size_mode="FIT_CONTENTS",
        theme="alpine",
        custom_css={
            "#gridToolBar": {"display": "none"},
        },
        allow_unsafe_jscode=True,
        height=500,
    )
    selection = doc_grid.get("selected_rows", [])
    return selection
