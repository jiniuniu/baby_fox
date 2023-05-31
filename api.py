import argparse
import os

import uvicorn
from fastapi import Body, FastAPI
from langchain.llms import OpenAI
from pydantic import BaseModel, Field

from baby_fox.chat_bot import ChatBot
from baby_fox.llms.chatglm import ChatGLM

# DOC_STORE_DIR = "/home/data/"


class BaseResponse(BaseModel):
    code: int = Field(200, description="HTTP status code")
    msg: str = Field("SUCCESS", description="HTTP status message")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "SUCCESS",
            }
        }


class Message(BaseModel):
    query: str = Field(..., description="query text")
    answer: str = Field(..., description="answer text")

    class Config:
        schema_extra = {"example": {"query": "AI你好", "answer": "用户你好"}}


async def chat(query: str = Body(..., description="query")):
    answer = chat_bot.answer_directly(query, chat_history_included=True)
    return Message(query=query, answer=answer)


# async def local_doc_chat(
#     doc_store_id: str = Body(..., description="document store id", example="ds-001"),
#     query: str = Body(..., description="query text", example="请介绍下复歌科技这家公司"),
# ):
#     doc_store_path = os.path.join(DOC_STORE_DIR, doc_store_id)
#     if not os.path.exists(doc_store_path):
#         return Message(query=query, answer=f"没有{doc_store_id}这个本地知识库")
#     else:
#         answer = chat_bot.answer_based_on_local_doc(
#             query, doc_store_path=doc_store_path
#         )

#     return Message(query=query, answer=answer)


def start_server(host, port):
    global app
    global chat_bot

    llm = OpenAI(temperature=0.0, model_name="gpt-3.5-turbo", max_tokens=2048)

    app = FastAPI()
    app.post("/chat", response_model=Message)(chat)
    chat_bot = ChatBot(llm)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="baby_fox", description="baby fox")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=27777)
    args = parser.parse_args()
    start_server(args.host, args.port)
