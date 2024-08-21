import json
from datetime import datetime

from message import Message


USER_ROLE = "user"
ASSIST_ROLE = "assistant"

class Conversation:
    def __init__(self):
        self._history: list[Message] = []
        self._system_prompt: str | None = None
        self._num_words: int = 0
        self._num_tokens: int = 0

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    @property
    def num_words(self) -> int:
        return self._num_words

    @num_words.setter
    def num_words(self, count: int) -> None:
        self._num_words = count

    @property
    def num_tokens(self) -> int:
        return self._num_tokens

    @num_tokens.setter
    def num_tokens(self, count: int) -> None:
        self._num_tokens = count

    def add_user_message(self, content: str):
        msg = Message(USER_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def add_assistant_message(self, content: str):
        msg = Message(ASSIST_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def construct_api_message(self) -> list:
        return [msg.to_dict() for msg in self._history]

    def save_conversation(self, desc: str) -> None:
        current_datetime = datetime.now()
        filename = current_datetime.strftime(f"conversations/{desc}_%Y%m%d_%H%M%S") + ".txt"
        with open(filename, 'w') as output_file:
            for message in self._history:
                output_file.write(json.dumps(message.to_dict()))
