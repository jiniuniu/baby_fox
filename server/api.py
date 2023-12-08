import argparse
import asyncio
from typing import Any, Awaitable

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.schema import LLMResult
from starlette.middleware.cors import CORSMiddleware

from agents.agent_loader import AgentLoader
from server.auth import get_token
from server.schemas import BaseResponse, ChatRequest, ChatResponse, ThoughtStep
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
async def agent_chat(chat_request: ChatRequest) -> ChatResponse:
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
    agent_message = response["output"]
    thought_steps = []
    intermediate_steps = response["intermediate_steps"]
    for intermediate_step in intermediate_steps:
        action_log = intermediate_step[0].log.strip()
        action_observation = intermediate_step[1]
        thought_steps.append(
            ThoughtStep(
                action_log=action_log,
                action_observation=action_observation,
            )
        )

    chat_response = ChatResponse(
        agent_message=agent_message,
        thought_steps=thought_steps,
    )

    return chat_response


async def wrap_done(fn: Awaitable, event: asyncio.Event):
    """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
    try:
        await fn
    except Exception as e:
        # TODO: handle exception
        print(f"Caught exception: {e}")
    finally:
        # Signal the aiter to stop.
        event.set()


class MyAsyncCallbackHandler(AsyncIteratorCallbackHandler):
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # Process the response object and extract the data you want to send
        # For example, you could extract the generated text from the response
        pass


@app.post("/agent_stream_chat")
async def agent_chat(chat_request: ChatRequest):
    stream_it = MyAsyncCallbackHandler()

    agent_key = chat_request.agent_key
    agent = AgentLoader.load_agent(agent_key, callbacks=[stream_it])
    if agent is None:
        return BaseResponse(
            code=404,
            msg=f"did not find agent with key: {agent_key}",
        )

    user_message = chat_request.user_message
    chat_history = chat_request.chat_history
    agent.memory.chat_memory = process_chat_history(chat_history)

    async def create_gen(query: str):
        task = asyncio.create_task(
            wrap_done(
                agent.acall({"input": query}),
                stream_it.done,
            )
        )
        async for token in stream_it.aiter():
            yield token
        await task

    gen = create_gen(user_message)
    return StreamingResponse(gen, media_type="text/event-stream")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7862)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
