"""Wrapper around ChatGLM APIs."""
from typing import List, Optional

import torch
from config import CHATGLM_6B_MODEL_PATH
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from pydantic import Extra
from transformers import AutoModel, AutoTokenizer

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


class ChatGLM(LLM):
    # 最多生成的token个数
    max_tokens: int = 2048
    # 表示使用的sampling temperature，更高的temperature意味着模型具备更多的可能性，适用于更有创造性的场景
    temperature: float = 0.0
    # 来源于nucleus sampling，采用的是累计概率的方式，0.1意味着只考虑由前10%累计概率组成的词汇
    top_p: float = 0.9
    # load pre-trained model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        CHATGLM_6B_MODEL_PATH, trust_remote_code=True
    )
    model = (
        AutoModel.from_pretrained(CHATGLM_6B_MODEL_PATH, trust_remote_code=True)
        .half()
        .cuda()
    )
    model.eval()

    class Config:
        extra = Extra.forbid

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response, _ = self.model.chat(
            self.tokenizer,
            prompt,
            history=[],
            max_length=self.max_tokens,
            top_p=self.top_p,
            temperature=self.temperature,
        )
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        torch_gc()
        return response
