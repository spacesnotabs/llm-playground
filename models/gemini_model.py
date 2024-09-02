from pathlib import Path

from .base_model import BaseModel
from .model_settings import ModelSettings
from tools.file_tools import gemini_tools, read_file, write_file

import google.generativeai as genai


class GeminiModel(BaseModel):
    MODEL_FLASH = "gemini-1.5-flash"
    MODEL_PRO = "gemini-1.5-pro"

    def __init__(self, api_key: str, settings: ModelSettings):
        super().__init__(settings=settings)

        config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=self._settings.max_tokens,
            temperature=self._settings.temperature
        )

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name=self._settings.model_id,
                                            generation_config=config,
                                            tools=[read_file, write_file])
        self._chat = self._model.start_chat(history=[], enable_automatic_function_calling=True)

    def send_message(self, contents: str) -> str:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(contents)

        response = self._chat.send_message(contents)
        print(response)

        self.conversation.add_system_message(response.text)

        if self._response_callback:
            self._response_callback(response.text)

        return response.text

    def clear_conversation(self) -> None:
        self._chat.history = []
        super().clear_conversation()

