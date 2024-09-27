from threading import Thread
from time import sleep
from typing import Callable, Dict, Optional

from jsonschema import validate, ValidationError
from enum import Enum

from models.base_model import BaseModel


class AgentState(Enum):
    """Enum representing the different states an agent can be in."""
    IDLE = 0
    PROCESSING = 1
    WAITING_FOR_USER = 2


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str, llm: Optional[BaseModel] = None):
        """
        Initializes the agent.

        :param name: The name of the agent.
        :param llm: The language model to use for the agent.
        """
        self._name: str = name
        self._llm: Optional[BaseModel] = llm
        self._agent_state: AgentState = AgentState.IDLE
        self._user_input_thread: Optional[Thread] = None
        self._user_input: Optional[Dict] = None
        self._send_user_message_callback: Optional[Callable[[str], None]] = None

    @property
    def agent_state(self) -> AgentState:
        """
        Returns the current state of the agent.

        :return: The current state of the agent.
        """
        return self._agent_state

    @agent_state.setter
    def agent_state(self, state: AgentState) -> None:
        """
        Sets the current state of the agent.

        :param state: The new state of the agent.
        """
        self._agent_state = state

    def run_agent(self, agent_input: Dict) -> Dict:
        """
        Runs the agent with the specified input.

        :param agent_input: Input data to the agent.
        :return: The output of the agent.
        """
        pass

    def request_user_input(self, message: str) -> None:
        """
        Requests user input from the user.

        :param message: The message to display to the user.
        """
        self.send_user_message(message)
        # start thread to wait for input
        self._user_input_thread = Thread(target=self._wait_for_user_input, daemon=True)
        self._user_input_thread.start()

    def user_input_received(self, user_input: Dict) -> None:
        """
        Handles user input received from the user.

        :param user_input: The user input.
        """
        self._user_input = user_input

    def _wait_for_user_input(self) -> None:
        """
        Waits for user input for a specified timeout.
        """
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
        """
        Sends a message to the user.

        :param message: The message to send.
        """
        if self._send_user_message_callback:
            self._send_user_message_callback(message)

    def validate_input(self, agent_input: Dict, schema: Dict) -> bool:
        """
        Validates the input data against the specified schema.

        :param agent_input: The input data.
        :param schema: The schema to validate against.
        :return: True if the input is valid, False otherwise.
        """
        try:
            validate(instance=agent_input, schema=schema)
            return True
        except ValidationError as e:
            print(f"Error validating input: {e}")
            return False

    def validate_output(self, agent_output: Dict, schema: Dict) -> bool:
        """
        Validates the output data against the specified schema.

        :param agent_output: The output data.
        :param schema: The schema to validate against.
        :return: True if the output is valid, False otherwise.
        """
        try:
            validate(instance=agent_output, schema=schema)
            return True
        except ValidationError as e:
            print(f"Error validating output: {e}")
            return False

    def clear_chat(self) -> Dict:
        """
        Clears the chat history.

        :return: A dictionary with the response.
        """
        if self._llm:
            self._llm.clear_conversation()

        return {"response": "Cleared chat history"}
