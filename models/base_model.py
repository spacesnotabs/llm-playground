from threading import Thread

from .model_settings import ModelSettings
from conversation import Conversation


class BaseModel:
    def __init__(self, settings: ModelSettings):
        self._settings: ModelSettings = settings
        self._conversation: Conversation | None = None
        self._run_thread: Thread | None = None
        self._stop: bool = False
        self._input_message: str | None = None
        self._response_callback = None
        self._create_conversation()
        self._system_prompt: str | None = None
        self._initial_prompt: str | None = None

    @property
    def conversation(self) -> Conversation:
        return self._conversation

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    @property
    def initial_prompt(self) -> str:
        return self._initial_prompt

    @initial_prompt.setter
    def initial_prompt(self, prompt: str) -> None:
        self._input_message = prompt
        self._initial_prompt = prompt

    @conversation.setter
    def conversation(self, conversation: Conversation) -> None:
        """
        If conversation already exists, save it and replace with new one
        :param conversation: new Conversation object
        :return: None
        """
        if not self._conversation:
            self._conversation = conversation
        else:
            self._conversation.save_conversation(self._settings.model_name)
            self._conversation = Conversation()

    def set_callback(self, func) -> None:
        self._response_callback = func

    def send_message(self, contents: str) -> str:
        pass

    def initialize(self) -> None:
        """
        Start the chatbot by sending the initial prompt to it.
        :return: None
        """
        pass

    def clear_conversation(self) -> None:
        """
        Clears the conversation history
        :return:
        """
        self.conversation.clear_conversation(save=True)

    def _create_conversation(self) -> None:
        self.conversation = Conversation()
