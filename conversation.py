import json
from datetime import datetime

from basicmessage import BasicMessage

SYSTEM_ROLE = "system"
USER_ROLE = "user"
ASSIST_ROLE = "assistant"


class Conversation:
    """
    Class that stores the conversation history.
    """
    def __init__(self):
        """
        Initializes a Conversation object.
        """
        self._history: list[BasicMessage] = []
        self._system_prompt: str | None = None
        self._num_words: int = 0
        self._num_tokens: int = 0

    @property
    def system_prompt(self) -> str:
        """
        Getter for the system prompt.
        """
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, prompt: str) -> None:
        """
        Setter for the system prompt.
        """
        self._system_prompt = prompt

    @property
    def num_words(self) -> int:
        """
        Getter for the number of words in the conversation.
        """
        return self._num_words

    @num_words.setter
    def num_words(self, count: int) -> None:
        """
        Setter for the number of words in the conversation.
        """
        self._num_words = count

    @property
    def num_tokens(self) -> int:
        """
        Getter for the number of tokens in the conversation.
        """
        return self._num_tokens

    @num_tokens.setter
    def num_tokens(self, count: int) -> None:
        """
        Setter for the number of tokens in the conversation.
        """
        self._num_tokens = count

    def add_system_message(self, content: str):
        """
        Adds a system message to the conversation history.
        """
        msg = BasicMessage(SYSTEM_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def add_user_message(self, content: str):
        """
        Adds a user message to the conversation history.
        """
        msg = BasicMessage(USER_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def add_assistant_message(self, content: str):
        """
        Adds an assistant message to the conversation history.
        """
        msg = BasicMessage(ASSIST_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def construct_api_message(self) -> list:
        """
        Constructs a list of dictionaries representing the conversation history.
        """
        return [msg.to_dict() for msg in self._history]

    def save_conversation(self, desc: str) -> None:
        """
        Saves the conversation history to a file.
        """
        current_datetime = datetime.now()
        filename = current_datetime.strftime(f"conversations/{desc}_%Y%m%d_%H%M%S") + ".txt"
        with open(filename, 'w') as output_file:
            for message in self._history:
                output_file.write(json.dumps(message.to_dict()))

    def clear_conversation(self, save: bool = False) -> None:
        """
        Clears the conversation history.
        """
        if save:
            self.save_conversation(desc='auto_save')

        self._history.clear()
