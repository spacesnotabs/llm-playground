from pathlib import Path

from google.ai.generativelanguage_v1 import Content, Part

from conversation import Conversation
from .base_model import BaseModel
from .model_settings import ModelSettings

import google.generativeai as genai


class GeminiModel(BaseModel):
    MODEL_FLASH = "gemini-1.5-flash"
    MODEL_PRO = "gemini-1.5-pro"

    def __init__(self, settings: ModelSettings):
        super().__init__(settings=settings)
        self._model: genai.GenerativeModel | None = None
        self._chat: genai.ChatSession | None = None
        self._stream = True

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
            self.post_message(f"Unable to create Gemini model due to exception: {e}")

    def send_message(self, contents: str) -> str:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(contents)

        try:
            response = self._chat.send_message(contents, stream=self._stream)
            if self._stream:
                for chunk in response:
                    if self._response_callback:
                        self._response_callback(chunk.text)

                if self._response_callback:
                    self._response_callback('[END]')

        except Exception as e:
            print("Gemini failed with exception: ", e)
            self.post_message(message=f"There was an exception when attempting to send a message to Gemini: {e}")
            return ""

        # print(response)

        self.conversation.add_system_message(response.text)

        if not self._stream:
            self.post_message(response.text)

        # print(self._chat.history)
        return response.text

    def clear_conversation(self) -> None:
        self._chat.history = []
        super().clear_conversation()

    def continue_conversation(self, conversation: Conversation):
        # print('continue_conversation: ', conversation)
        self.conversation = conversation

        chat_history = []
        for message in conversation.construct_api_message():
            content = Content()
            content.role = message['role']
            part = Part()
            part.text = message['content']
            content.parts.append(part)
            chat_history.append(content)

        # print(chat_history)
        self._chat.history = chat_history
        # print(self._chat.history)