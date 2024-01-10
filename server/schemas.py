from enum import Enum
from typing import Dict, List

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


class XhsIdeasRequest(BaseModel):
    product_name: str = Field(..., description="产品名称")
    selling_points: str = Field(..., description="产品的卖点功效")


class XhsGenNoteRequest(BaseModel):
    category_name: str = Field(..., description="品类名称")
    product_name: str = Field(..., description="产品名称")
    user_role: str = Field(..., description="人设")
    scence: str = Field(..., description="场景")
    information_channel: str = Field(..., description="信息渠道")
    usage_experience: str = Field(..., description="使用感受")
    usage_effect: str = Field(..., description="使用效果")
    other_requirements: str = Field(..., description="其他要求")
