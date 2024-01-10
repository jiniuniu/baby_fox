import argparse
import asyncio
from typing import Dict

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from starlette.middleware.cors import CORSMiddleware

from agents.agent_loader import AgentConfig, AgentLoader
from agents.db.repository import list_all
from chains import build_xhs_chain_by_type
from chains.xhs.data_source import get_general_keywords, get_xhs_note
from server.auth import get_token
from server.schemas import (
    AgentInfo,
    AgentsInfosResponse,
    BaseResponse,
    ChatRequest,
    ChatResponse,
    ThoughtStep,
    XhsGenNoteRequest,
    XhsIdeasRequest,
)
from server.utils import MyAsyncCallbackHandler, process_chat_history, wrap_done

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


@app.get("/list_agents")
async def list_agents() -> AgentsInfosResponse:
    agent_config_data = list_all()
    res = []
    for key, agent_config_str in agent_config_data.items():
        agent_config = AgentConfig.model_validate_json(agent_config_str)
        agent_name = agent_config.name
        description = agent_config.description
        agent_info = AgentInfo(
            key=key,
            name=agent_name,
            description=description,
        )
        res.append(agent_info)
    return AgentsInfosResponse(agents_infos=res)


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


@app.post("/agent_stream_chat")
async def agent_stream_chat(chat_request: ChatRequest):
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


@app.post("/xhs_ideas")
async def generate_xhs_ideas(xhs_ideas_req: XhsIdeasRequest):
    stream_it = AsyncIteratorCallbackHandler()
    idea_generator = build_xhs_chain_by_type(
        chain_type="xhs_ideas",
        callbacks=[stream_it],
    )
    product_name = xhs_ideas_req.product_name
    selling_points = xhs_ideas_req.selling_points

    inp = {
        "product_name": product_name,
        "selling_points": selling_points,
    }

    async def create_gen(inp: Dict):
        task = asyncio.create_task(
            wrap_done(
                idea_generator.acall(inp),
                stream_it.done,
            )
        )
        async for token in stream_it.aiter():
            yield token
        await task

    gen = create_gen(inp)
    return StreamingResponse(gen, media_type="text/event-stream")


@app.post("/xhs_gen_note_from_idea")
async def generate_xhs_note_from_idea(xhs_gen_note_req: XhsGenNoteRequest):
    stream_it = AsyncIteratorCallbackHandler()
    note_creator = build_xhs_chain_by_type(
        chain_type="xhs_note_creator",
        callbacks=[stream_it],
    )
    product_name = xhs_gen_note_req.product_name
    category_name = xhs_gen_note_req.category_name
    user_role = xhs_gen_note_req.user_role
    scence = xhs_gen_note_req.scence
    information_channel = xhs_gen_note_req.information_channel
    usage_experience = xhs_gen_note_req.usage_experience
    usage_effect = xhs_gen_note_req.usage_effect
    other_requirements = xhs_gen_note_req.other_requirements

    note_data = get_xhs_note(category_name)
    title = note_data.get("title") or ""
    content = note_data.get("content") or ""
    case_keywords = note_data.get("case_keywords") or []
    case_keywords = "\n".join(case_keywords)
    general_keywords = get_general_keywords()
    general_keywords = "\n".join(general_keywords)

    inp = {
        "user_role": user_role,
        "scence": scence,
        "information_channel": information_channel,
        "usage_experience": usage_experience,
        "usage_effect": usage_effect,
        "other_requirements": other_requirements,
        "general_keywords": general_keywords,
        "case_keywords": case_keywords,
        "title": title,
        "content": content,
        "product_name": product_name,
    }

    async def create_gen(inp: Dict):
        task = asyncio.create_task(
            wrap_done(
                note_creator.acall(inp),
                stream_it.done,
            )
        )
        async for token in stream_it.aiter():
            yield token
        await task

    gen = create_gen(inp)
    return StreamingResponse(gen, media_type="text/event-stream")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7862)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
