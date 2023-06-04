import argparse
import os
import shutil
from typing import List, Optional

import uvicorn
from fastapi import Body, FastAPI, File, Form, Query, UploadFile
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse
from typing_extensions import Annotated

from baby_fox.chat_bot import ChatBot
from baby_fox.config import *
from baby_fox.llms.chatglm_api import ChatGLMApi
from baby_fox.logger import setup_logger

log = setup_logger(file_path=LOG_FILE_PATH)


async def document():
    return RedirectResponse(url="/docs")


class BaseResponse(BaseModel):
    code: int = Field(200, description="HTTP status code")
    msg: str = Field("success", description="HTTP status message")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }


class ListDocsResponse(BaseResponse):
    data: List[str] = Field(..., description="A list of documents names")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": ["doc1.docx", "doc2.pdf", "doc3.txt"],
            }
        }


class Message(BaseModel):
    query: str = Field(..., description="query text")
    answer: str = Field(..., description="answer text")
    sources: List[str] = Field(..., description="A list of source documents")

    class Config:
        schema_extra = {
            "example": {
                "query": "AI你好",
                "answer": "用户你好",
                "sources": ["出处 [1] ...", "出处 [2] ...", "出处 [3] ..."],
            }
        }


async def chat(query: str = Body(..., description="query")) -> Message:
    answer = chat_bot.answer_directly(query, chat_history_included=True)
    return Message(query=query, answer=answer, sources=[])


async def upload_files(
    files: Annotated[
        List[UploadFile], File(description="Multiple files as UploadFile")
    ],
    knowledge_name: str = Form(
        ..., description="上传文件到的知识库名", example="fugetech_company_info"
    ),
) -> BaseResponse:
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
        loaded_files = chat_bot.build_index(filelist, knowledge_name)
        if loaded_files:
            file_status = f"已上传 {'、'.join([os.path.split(i)[-1] for i in loaded_files])} 至知识库，并已加载知识库，请开始提问"
            return BaseResponse(code=200, msg=file_status)
    file_status = "文件未成功加载，请重新上传文件"
    return BaseResponse(code=500, msg=file_status)


async def list_files(
    knowledge_name: str = Query(
        default=None, description="罗列知识库名下的文件", example="fugetech_company_info"
    )
) -> ListDocsResponse:
    file_dir = os.path.join(FILES_ROOT, knowledge_name)
    if not os.path.exists(file_dir):
        return ListDocsResponse(code=1, msg=f"没有找到知识库：{knowledge_name}", data=[])
    filenames = []
    for obj in os.listdir(file_dir):
        if os.path.isfile(os.path.join(file_dir, obj)):
            filenames.append(obj)
    return ListDocsResponse(data=filenames)


async def delete_files(
    knowledge_name: str = Query(
        ...,
        description="知识库名，删除该知识库下的文件（不会删除相应的索引）",
        example="fugetech_company_info",
    ),
    filename: Optional[str] = Query(
        None, description="文件名（删除知识库下的文件）", example="doc1.pdf"
    ),
) -> BaseResponse:
    file_dir = os.path.join(FILES_ROOT, knowledge_name)
    if not os.path.exists(file_dir):
        return BaseResponse(code=1, msg=f"没有找到知识库：{knowledge_name}")
    if filename:
        file_path = os.path.join(file_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return BaseResponse(msg=f"文件：{filename} 删除成功")
        else:
            return BaseResponse(code=1, msg=f"没有找到文件：{filename}")
    else:
        shutil.rmtree(file_dir)
        return BaseResponse(code=200, msg=f"知识库：{knowledge_name} 删除成功")


async def local_knowledge_chat(
    knowledge_name: str = Body(
        ..., description="知识库名称", example="fugetech_company_info"
    ),
    question: str = Body(..., description="知识库相关提问", example="介绍下复歌科技的团队文化"),
) -> Message:
    index_path = os.path.join(INDEX_ROOT, knowledge_name)
    if not os.path.exists(index_path):
        return Message(query=question, answer=f"没有找到知识索引库：{knowledge_name}", sources=[])

    answer, sources = chat_bot.answer_with_local_sources(question, index_path)
    return Message(query=question, answer=answer, sources=sources)


def start_server(host: str, port: int) -> None:
    global app
    global chat_bot

    app = FastAPI()
    app.get("/", response_model=BaseResponse)(document)
    app.post("/chat", response_model=Message)(chat)
    app.post("/local_knowledge/chat", response_model=Message)(local_knowledge_chat)
    app.post("/local_knowledge/upload", response_model=BaseResponse)(upload_files)
    app.get("/local_knowledge/list_files", response_model=ListDocsResponse)(list_files)
    app.post("/local_knowledge/delete", response_model=BaseResponse)(delete_files)
    chat_bot = ChatBot()
    chat_bot.llm = ChatGLMApi()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="baby_fox", description="baby fox")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=27777)
    args = parser.parse_args()
    start_server(args.host, args.port)
