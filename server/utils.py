from typing import Any

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.schema import LLMResult
from loguru import logger

from server.schemas import Message, Role


def process_chat_history(chat_history: list[Message]) -> ChatMessageHistory:
    msgs = ChatMessageHistory()
    for message in chat_history:
        if message.role == Role.USER:
            msgs.add_user_message(message.content)
        else:
            msgs.add_ai_message(message.content)
    return msgs


# class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
#     content: str = ""
#     final_answer: bool = False

#     def __init__(self) -> None:
#         super().__init__()

#     async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
#         self.content += token
#         # if we passed the final answer, we put tokens in queue
#         if self.final_answer:
#             if '"action_input": "' in self.content:
#                 if token not in ['"', "}"]:
#                     self.queue.put_nowait(token)
#         elif "Final Answer" in self.content:
#             self.final_answer = True
#             self.content = ""

#     async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
#         if self.final_answer:
#             self.content = ""
#             self.final_answer = False
#             self.done.set()
#         else:
#             self.content = ""
