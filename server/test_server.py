import json

import requests
from loguru import logger

from server.config import env_settings

AGENT_CHAT_URL = "http://127.0.0.1:7862/agent_stream_chat"
IDEA_URL = "http://127.0.0.1:7862/xhs_ideas"
CREATOR_URL = "http://127.0.0.1:7862/xhs_gen_note_from_idea"
CREATOR_V2_URL = "http://127.0.0.1:7862/xhs_gen_note"

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


def test_idea_chain():
    input_data = {
        "product_name": "Olay淡斑小白瓶",
        "selling_points": "淡斑",
    }
    res = ""
    try:
        with requests.post(
            headers=HEADERS,
            data=json.dumps(
                input_data,
                ensure_ascii=False,
            ).encode("utf-8"),
            url=IDEA_URL,
            stream=True,
        ) as response:
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=1024):
                if not chunk:
                    break

                chunk = chunk.decode("'utf-8'")
                print(chunk, end="")
                res += chunk
    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
    return res


def test_creator_chain():
    input_data = {
        "category_name": "抗老精华",
        "product_name": "Olay淡斑小白瓶",
        "user_role": "45岁的企业女高管，长期工作压力大，面临肌肤老化",
        "scence": "面对镜子时，发现眼角和额头的细纹越来越多",
        "information_channel": "在朋友聚会上，听朋友分享Olay淡斑小白瓶的效果",
        "usage_experience": "质地细腻，涂抹后感觉肌肤更加紧致，没有紧绷感",
        "usage_effect": "持续使用两个月，细纹有所减少，肌肤感觉更加有弹性",
        "other_requirements": "除了使用抗老产品，建议每周进行至少一次的面部按摩，以促进血液循环和肌肤弹性",
    }
    res = ""
    try:
        with requests.post(
            headers=HEADERS,
            data=json.dumps(
                input_data,
                ensure_ascii=False,
            ).encode("utf-8"),
            url=CREATOR_URL,
            stream=True,
        ) as response:
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=1024):
                if not chunk:
                    break

                chunk = chunk.decode("'utf-8'")
                print(chunk, end="")
                res += chunk
    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
    return res


def test_creator_chain_v2():
    input_data = {
        "category_name": "抗老精华",
        "product_name": "Olay淡斑小白瓶",
        "selling_points": "淡斑、美白、抗衰老",
    }
    res = ""
    try:
        with requests.post(
            headers=HEADERS,
            data=json.dumps(
                input_data,
                ensure_ascii=False,
            ).encode("utf-8"),
            url=CREATOR_V2_URL,
            stream=True,
        ) as response:
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=1024):
                if not chunk:
                    break

                chunk = chunk.decode("'utf-8'")
                print(chunk, end="")
                res += chunk
    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
    return res


if __name__ == "__main__":
    # q = "请做自我介绍"
    # q = "72 加 15 之后再除以 2 等于多少"
    res = test_creator_chain_v2()
    print("\n" + res)
