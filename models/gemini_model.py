from pathlib import Path

from .base_model import BaseModel
from .model_settings import ModelSettings
from tools.file_tools import gemini_tools, read_file, write_file

import google.generativeai as genai


class GeminiModel(BaseModel):
    MODEL_FLASH = "gemini-1.5-flash"
    MODEL_PRO = "gemini-1.5-pro"

    def __init__(self, settings: ModelSettings):
        super().__init__(settings=settings)
        self._model: genai.GenerativeModel | None = None
        self._chat: genai.ChatSession | None = None

    def initialize(self) -> None:
        config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=self._settings.max_tokens,
            temperature=self._settings.temperature
        )

        genai.configure(api_key=self._settings.api_key)
        self._model = genai.GenerativeModel(model_name=self._settings.model_id,
                                            generation_config=config,
                                            system_instruction=self.system_prompt)

        try:
            self._chat = self._model.start_chat(history=[])
        except Exception as e:
            print("Unable to create Gemini model due to exception: ", e)

    def send_message(self, contents: str) -> str:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(contents)

        try:
            response = self._chat.send_message(contents)
        except Exception as e:
            print("Gemini failed with exception: ", e)
            return ""

        # print(response)

        self.conversation.add_system_message(response.text)

        if self._response_callback:
            self._response_callback(response.text)

        return response.text

    def clear_conversation(self) -> None:
        self._chat.history = []
        super().clear_conversation()

