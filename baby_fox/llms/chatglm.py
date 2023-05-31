"""Wrapper around ChatGLM APIs."""
import json
from typing import List, Optional

import requests
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from pydantic import Extra


class ChatGLM(LLM):
    """Wrapper around ChatGLM API."""

    # 最多生成的token个数
    max_tokens: int = 2048
    # 表示使用的sampling temperature，更高的temperature意味着模型具备更多的可能性，适用于更有创造性的场景
    temperature: float = 0.0
    # 来源于nucleus sampling，采用的是累计概率的方式，0.1意味着只考虑由前10%累计概率组成的词汇
    top_p: float = 0.9
    # endpoint url
    # 部署一个GPU的推理服务，通过 http request 访问
    endpoint = ""

    class Config:
        extra = Extra.forbid

    def _llm_type(self) -> str:
        return "chatglm_type"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        body = {
            "prompt": prompt,
            "history": [],
            "temperture": self.temperature,
            "top_p": self.top_p,
            "max_length": self.max_tokens,
        }
        headers = {"Content-type": "application/json"}
        try:
            resp = requests.post(self.endpoint, headers=headers, json=body)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        if resp.status_code != 200:
            raise Exception(
                f"Error: {resp.status_code} {resp.reason} {resp.text}",
            )
        resp_dict = json.loads(resp.text)
        response = resp_dict["response"]
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        return response


if __name__ == "__main__":
    llm = ChatGLM()
    prompt = "法国大革命的时代背景"
    res = llm(prompt)
    print(res)
