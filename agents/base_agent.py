from threading import Thread
from time import sleep
from typing import Callable

from jsonschema import validate, ValidationError
from enum import Enum

from models.base_model import BaseModel

class AgentState(Enum):
    IDLE = 0
    PROCESSING = 1
    WAITING_FOR_USER = 2

class BaseAgent:
    def __init__(self, name: str, llm: BaseModel | None = None):
        self._name: str = name
        self._llm: BaseModel = llm
        self._agent_state = AgentState.IDLE
        self._user_input_thread: Thread | None = None
        self._user_input: dict | None = None
        self._send_user_message_callback: Callable[[str], None] | None = None

    @property
    def agent_state(self) -> AgentState:
        return self._agent_state

    @agent_state.setter
    def agent_state(self, state: AgentState) -> None:
        self._agent_state = state

    def run_agent(self, agent_input: dict) -> dict:
        """
        Runs the agent with the specified input
        :param agent_input: input data to the agent
        :return: the output of the agent
        """
        pass

    def request_user_input(self, message: str) -> None:
        self.send_user_message(message)
        # start thread to wait for input
        self._user_input_thread = Thread(target=self._wait_for_user_input, daemon=True)
        self._user_input_thread.start()

    def user_input_received(self, user_input: dict) -> None:
        self._user_input = user_input

    def _wait_for_user_input(self) -> None:
        timeout = 30
        delay = 1
        while True:
            if self._user_input:
                break
            if timeout <= 0:
                break

            sleep(delay)
            timeout -= delay

    def send_user_message(self, message: str) -> None:
        if self._send_user_message_callback:
            self._send_user_message_callback(message)

    def validate_input(self, agent_input: dict, schema: dict) -> bool:
        try:
            validate(instance=agent_input, schema=schema)
            return True
        except ValidationError as e:
            print("Error validating input: ", e)
            return False

    def validate_output(self, agent_output: dict, schema: dict) -> bool:
        try:
            validate(instance=agent_output, schema=schema)
            return True
        except ValidationError as e:
            print("Error validating output: ", e)
            return False

    def clear_chat(self) -> dict:
        if self._llm:
            self._llm.clear_conversation()

        return {"response": "Cleared chat history"}
