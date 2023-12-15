import asyncio
from typing import Any, Awaitable

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.schema import LLMResult

from server.schemas import Message, Role


def process_chat_history(chat_history: list[Message]) -> ChatMessageHistory:
    msgs = ChatMessageHistory()
    for message in chat_history:
        if message.role == Role.USER:
            msgs.add_user_message(message.content)
        else:
            msgs.add_ai_message(message.content)
    return msgs


class MyAsyncCallbackHandler(AsyncIteratorCallbackHandler):
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # Process the response object and extract the data you want to send
        # For example, you could extract the generated text from the response
        pass


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
