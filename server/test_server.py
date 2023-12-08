import json

import requests
from loguru import logger

from server.config import env_settings

AGENT_CHAT_URL = "http://127.0.0.1:7862/agent_stream_chat"

TOKEN = env_settings.KNOWN_ACCESS_TOKEN
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}


def process_response(prompt: str, selected_agent_key: str):
    input_data = {
        "user_message": prompt,
        "agent_key": selected_agent_key,
        "chat_history": [],
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

            for line in response.iter_lines():
                line = line.decode("'utf-8'")
                print(line, end="\n")

    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")


if __name__ == "__main__":
    # q = "请做自我介绍"
    # q = "72 加 15 之后再除以 2 等于多少"
    q = "做一个上海的旅游攻略"
    agent_key = "002"
    process_response(q, agent_key)
