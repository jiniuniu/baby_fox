import argparse

import pandas as pd

from agents.db.repository import add_or_update_to_db

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_file_path")
    args = parser.parse_args()
    csv_file_path = args.csv_file_path
    df = pd.read_csv(
        csv_file_path,
        dtype={
            "agent_key": str,
            "agent_config": str,
        },
    )
    for row in df.itertuples():
        _, key, agent_config = row
        add_or_update_to_db(key, agent_config)
