from anthropic import Anthropic

from .base_agent import BaseAgent
from .agent_settings import AgentSettings

class AnthropicAgent(BaseAgent):

    MODEL_HAIKU = "claude-3-haiku-20240307"
    MODEL_SONNET = "claude-3-sonnet-20240229"
    MODEL_SONNET_3_5 = "claude-3-5-sonnet-20240620"
    MODEL_OPUS = "claude-3-opus-20240229"

    def __init__(self, api_key: str, settings: AgentSettings):
        super().__init__(settings=settings)
        self._client = Anthropic(api_key=api_key)

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

    def send_message(self, contents: str) -> None:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(contents)

        response = self._client.messages.create(model=self._settings.model_name,
                                                max_tokens=self._settings.max_tokens,
                                                system=self._system_prompt if self._system_prompt else "",
                                                messages=self.conversation.construct_api_message(),
                                                temperature=self._settings.temperature,
                                                top_k=500
                                                )

        if response.stop_reason == "end_turn":
            response_text = response.content[0].text
            self._conversation.num_tokens += response.usage.input_tokens
            self._conversation.num_tokens += response.usage.output_tokens
            self._conversation.add_assistant_message(response_text)

            if self._response_callback:
                self._response_callback(response_text)

