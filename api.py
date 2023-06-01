import argparse
import os
from typing import List

import uvicorn
from fastapi import Body, FastAPI, File, Form, Query, UploadFile, WebSocket
from langchain.llms import OpenAI
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from baby_fox.chat_bot import ChatBot
from baby_fox.config import *
from baby_fox.index.index_builder import IndexBuilder
from baby_fox.llms.chatglm import ChatGLM
from baby_fox.logger import setup_logger

log = setup_logger(file_path=LOG_FILE_PATH)


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


async def upload_files(
    files: Annotated[
        List[UploadFile], File(description="Multiple files as UploadFile")
    ],
    knowledge_name: str = Form(
        ..., description="Knowledge_name", example="knowledge_about_fugetech"
    ),
):
    file_dir = os.path.join(FILES_ROOT, knowledge_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filelist = []
    for file in files:
        file_content = ""
        file_path = os.path.join(file_dir, file.filename)
        file_content = file.file.read()
        if os.path.exists(file_path) and os.path.getsize(file_path) == len(
            file_content
        ):
            continue
        with open(file_path, "ab+") as f:
            f.write(file_content)
        filelist.append(file_path)
    if filelist:
        loaded_files = IndexBuilder.build_index(filelist, knowledge_name)
        if loaded_files:
            file_status = f"已上传 {'、'.join([os.path.split(i)[-1] for i in loaded_files])} 至知识库，并已加载知识库，请开始提问"
            return BaseResponse(code=200, msg=file_status)
    file_status = "文件未成功加载，请重新上传文件"
    return BaseResponse(code=500, msg=file_status)


def start_server(host, port):
    global app
    global chat_bot

    llm = OpenAI(temperature=0.0, model_name="gpt-3.5-turbo", max_tokens=2048)

    app = FastAPI()
    app.post("/chat", response_model=Message)(chat)
    app.post("/local_doc_qa/upload", response_model=BaseResponse)(upload_files)
    chat_bot = ChatBot(llm)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="baby_fox", description="baby fox")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=27777)
    args = parser.parse_args()
    start_server(args.host, args.port)
