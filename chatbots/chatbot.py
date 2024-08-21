import time
from threading import Thread

from anthropic import Anthropic

from conversation import Conversation
from message import Message


class ChatBot:
    def __init__(self, name: str, api_key: str, model: str, max_tokens: int):
        self._name: str = name
        self._conversation: Conversation | None = None
        self._client = Anthropic(api_key=api_key)
        self._run_thread: Thread | None = None
        self._stop: bool = False
        self._input_message: str | None = None
        self._model: str = model
        self._max_tokens: int = max_tokens
        self._response_callback = None
        self._create_conversation()
        self._system_prompt: str = None
        self._initial_prompt: str = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def conversation(self) -> Conversation:
        return self._conversation

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
            self._conversation.save_conversation(self.name)
            self._conversation = Conversation()

    def set_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    def set_callback(self, func) -> None:
        print("Setting response callback ", self._response_callback)
        self._response_callback = func

    def send_message(self, contents: str) -> None:
        self._input_message = contents

    def initialize(self) -> None:
        """
        Start the chatbot by sending the initial prompt to it.
        :return: None
        """
        response = self._send_prompt()  # send the initial prompt
        if response.stop_reason == "end_turn":
            response_text = response.content[0].text
            self._conversation.num_tokens += response.usage.input_tokens
            self._conversation.num_tokens += response.usage.output_tokens
            self._conversation.add_assistant_message(response_text)
            self._input_message = None

    def start_bot(self) -> None:
        """
        Starts the chat bots thread
        :return:
        """
        print("Starting bot ", self._name)
        self._run_thread = Thread(target=self.run).start()

    def stop_bot(self) -> None:
        self._stop = True

    def run(self) -> None:
        print("Running bot ", self._name)
        retry = False
        while not self._stop:
            time.sleep(12)

            # print(f"Bot {self._name} has input message {self._input_message}")
            if self._input_message:
                if not retry:
                    response = self._send_prompt()

                # if response.stop_reason == "tool_use":
                #     tool_use = response.content[-1]
                #     tool_name = tool_use.name
                #     tool_input = tool_use.input
                #
                #     if tool_name == "email":
                #         tool_email(tool_input["contents"])
                if response.stop_reason == "end_turn":
                    response_text = response.content[0].text
                    self._conversation.num_tokens += response.usage.input_tokens
                    self._conversation.num_tokens += response.usage.output_tokens
                    self._conversation.add_assistant_message(response_text)
                    self._input_message = None
                    retry = False

                    if self._response_callback:
                        self._response_callback(response_text)
                else:
                    print("Retrying message due to ", response.stop_reason)
                    retry = True

        # thread was stopped
        return

    def _send_prompt(self) -> Message:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(self._input_message)

        response = self._client.messages.create(model=self._model,
                                                max_tokens=self._max_tokens,
                                                system=self._system_prompt if self._system_prompt else "",
                                                messages=self._conversation.construct_api_message(),
                                                temperature=1,
                                                top_k=500
                                                )
        return response

    def _create_conversation(self) -> None:
        self.conversation = Conversation()
