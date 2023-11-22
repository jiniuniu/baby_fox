from typing import List

from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from loguru import logger
from pydantic import BaseModel

from agents.db.repository import get_from_db
from agents.tools import TOOL_MAP
from agents.tools.searcher import BabyFoxSearchTool
from server.config import env_settings


class AgentConfig(BaseModel):
    name: str
    description: str
    instructions: str
    tool_names: List[str] = []
    model: str = "gpt-4-1106-preview"


class AgentLoader:
    @staticmethod
    def load_agent(agent_key: str) -> AgentExecutor:
        agent_config_str = get_from_db(agent_key)
        if agent_config_str is None:
            logger.info(f"can not find agent with key: {agent_key}")
            return
        agent_config = AgentConfig.model_validate_json(agent_config_str)
        instructions = agent_config.instructions
        tool_names = agent_config.tool_names
        model = agent_config.model
        llm = ChatOpenAI(
            model=model,
            api_key=env_settings.OPENAI_API_KEY,
        )
        tools = [
            BabyFoxSearchTool(),
        ]
        for tool_name in tool_names:
            tools.append(TOOL_MAP[tool_name])
        agent_kwargs = {
            "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
            "system_message": SystemMessage(content=instructions),
        }

        msgs = ChatMessageHistory()

        memory = ConversationBufferMemory(
            chat_memory=msgs,
            return_messages=True,
            memory_key="memory",
            input_key="input",
            output_key="output",
        )

        agent = initialize_agent(
            tools,
            llm,
            max_iterations=3,
            agent=AgentType.OPENAI_FUNCTIONS,
            agent_kwargs=agent_kwargs,
            memory=memory,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

        return agent
