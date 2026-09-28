import json
from dataclasses import asdict

from project.domain.message import UserMessage, MessageType, BotMessage
from project.domain.state import Turn


class HistoryBuilder:

    @staticmethod
    def build(turns: list[Turn]) -> str:
        messages: list[str] = []
        for turn in turns:
            user_message = HistoryBuilder.render_user_message(turn.user_message)
            messages.append(user_message)
            for bot_message in turn.bot_message:
                bot_message = HistoryBuilder.render_bot_message(bot_message)
                messages.append(bot_message)
        return "\n".join(messages)

    @staticmethod
    def render_user_message(user_message: UserMessage) -> str:
        if user_message.type == MessageType.TEXT:
            return f"USER: {user_message.text}"
        else:
            return f"USER: {json.dumps(asdict(user_message.object), ensure_ascii=False)}"

    @staticmethod
    def render_bot_message(bot_message: BotMessage) -> str:
        if bot_message.text:
            return f"BOT: {bot_message.text}"
        else:
            return f"BOT: {json.dumps(asdict(bot_message.object), ensure_ascii=False)}"
