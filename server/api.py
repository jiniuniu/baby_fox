import argparse
import json

import uvicorn
from fastapi import Depends, FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from agents.agent_loader import AgentLoader
from server.auth import get_token
from server.schemas import BaseResponse, ChatRequest, ChatResponse
from server.utils import process_chat_history

deps = [Depends(get_token)]

app = FastAPI(dependencies=deps)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=["*"],
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent_chat")
async def agent_chat(chat_request: ChatRequest) -> BaseResponse:
    agent_key = chat_request.agent_key
    agent = AgentLoader.load_agent(agent_key)
    if agent is None:
        return BaseResponse(
            code=404,
            msg=f"did not find agent with key: {agent_key}",
        )
    user_message = chat_request.user_message
    chat_history = chat_request.chat_history
    agent.memory.chat_memory = process_chat_history(chat_history)
    inp = {"input": user_message}
    response = agent(inp)
    logger.info(f"agent response: {response}")
    agent_message = response["output"]
    return ChatResponse(agent_message=agent_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7862)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
