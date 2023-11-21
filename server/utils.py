from langchain.memory.chat_message_histories import ChatMessageHistory

from server.schemas import Message, Role


def process_chat_history(chat_history: list[Message]) -> ChatMessageHistory:
    msgs = ChatMessageHistory()
    for message in chat_history:
        if message.role == Role.USER:
            msgs.add_user_message(message.content)
        else:
            msgs.add_ai_message(message.content)
    return msgs
