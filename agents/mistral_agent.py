from pathlib import Path

from .base_agent import BaseAgent
from .agent_settings import AgentSettings
import time

from llama_cpp import Llama

class MistralAgent(BaseAgent):
    def __init__(self, model_dir: Path, settings: AgentSettings):
        super().__init__(settings=settings)

        self._model = Llama(model_path=str(model_dir),
                            verbose=False,
                            max_tokens=self._settings.max_tokens,
                            n_gpu_layers=32,
                            n_batch=256,
                            n_threads=256,
                            n_threads_batch=256,
                            n_ctx=32000)

    def initialize(self) -> None:
        """
        Start the chatbot by sending the initial prompt to it.
        :return: None
        """
        response = self._send_prompt()  # send the initial prompt
        self._conversation.add_assistant_message(response)
        self._input_message = None


    def send_message(self, contents: str) -> None:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(contents)
        response = self._model.create_chat_completion(
            messages=self._conversation.construct_api_message(),
            max_tokens=self._settings.max_tokens,  # Limit the length of the output
            temperature=self._settings.temperature,  # Control the creativity of the model (0.0-1.0)
            # top_p=0.9  # Use nucleus sampling to limit the highest-probability tokens
        )

        response_text = response['choices'][0]['message']['content']
        self.conversation.add_system_message(response_text)

        if self._response_callback:
            self._response_callback(response_text)

