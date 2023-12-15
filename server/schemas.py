from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Role(str, Enum):
    USER: str = "user"
    ASSISTANT: str = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ThoughtStep(BaseModel):
    action_log: str
    action_observation: str


class BaseResponse(BaseModel):
    code: int = Field(200, description="API status code")
    msg: str = Field("success", description="API status message")


class ChatRequest(BaseModel):
    user_message: str = Field(..., description="user_message")
    agent_key: str = Field(..., description="agent_key")
    chat_history: List[Message] = Field([], description="chat_history")


class ChatResponse(BaseResponse):
    agent_message: str = Field(..., description="agent message")
    thought_steps: List[ThoughtStep] = Field(..., description="agent thought steps")


class AgentInfo(BaseModel):
    key: str = Field(..., description="agent key")
    name: str = Field(..., description="agent's name")
    description: str = Field(..., description="agent's description")


class AgentsInfosResponse(BaseResponse):
    agents_infos: List[AgentInfo] = Field(..., description="agents' infos")
