import json
import random
from typing import List

import requests
from loguru import logger

from server.config import env_settings

KB_ENDPOINT = env_settings.MARTECH_KB_ENDPOINT + "/xhs_notes_query"
KB_TOKEN = env_settings.MARTECH_KB_TOKEN
HEADERS = {
    "Authorization": f"Bearer {KB_TOKEN}",
}

GENERAL_KEYWORDS = [
    "经常有姐妹问我",
    "忍不住来分享",
    "别提了",
    "谁能懂啊",
    "咋说呢",
    "咋说捏",
    "妈呀，上个月",
    "吹爆",
    "Emmmm～",
    "离大谱",
    "亲测有效",
    "真的绝了",
    "真的狠！",
    "出乎意料的顶啊啊啊！",
    "难不心动咧",
    "都给我去！",
    "杀疯了",
    "全都搞定！",
    "跟**说拜拜",
    "成功上岸啦！",
    "真的很香",
    "这玩意",
    "TA",
    "这东西",
    "贼好用",
    "绝了",
    "尊嘟很不错",
    "好用的很突出",
    "真让我上头",
    "都给我用",
    "这么直观感受到",
    "人生建议",
    "巨巨巨牛",
    "讲真！",
    "太邪门了！都给我去使",
    "真的很赞",
    "拜托它真的很好用欸",
    "不是吧？",
    "啥呀！",
    "玩明白了",
    "我靠",
    "我K",
    "没想过这玩意这么",
    "救大命了",
    "vocal",
    "该不会还有人不知道吧",
    "诚不欺我",
    "被种草了",
    "无条件吃安利",
    "早知道就好了",
    "讲真的",
    "听劝",
    "告诉全世界真的行！",
    "看着**就够了",
    "家人们",
    "小红书姐妹们",
    "盆友们",
    "贼拉",
    "超级",
    "啊啊啊啊",
    "巨巨巨",
    "真真真的有用👍",
    "yyds！",
    "真的该拉黑！",
    "别跟风了",
    "对不起，不行！",
    "真的心累…",
    "能劝一个是一个！",
    "反复给我看！",
    "真心希望**都看到这篇！！",
    "真的烦死了！",
    "谁顶得住。。",
    "又又又又**了",
    "拿什么拯救",
    "令人心碎",
    "谁家好人像我一样",
    "心态崩了…",
    "我很是头大！",
]


def get_general_keywords() -> List[str]:
    general_keywords = random.choices(GENERAL_KEYWORDS, k=5)
    return general_keywords


def get_xhs_note(topic_name: str):
    try:
        resp = requests.post(
            headers=HEADERS,
            params={"topic_name": topic_name},
            url=KB_ENDPOINT,
        )
        resp.raise_for_status()
        resp = resp.json()
        logger.info(resp)
    except requests.RequestException as e:
        logger.error(f"Error during requests: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
    return resp
