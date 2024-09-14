from pathlib import Path

from .base_model import BaseModel
from .model_settings import ModelSettings

from llama_cpp import Llama


class PhiModel(BaseModel):
    def __init__(self, model_dir: Path, settings: ModelSettings):
        super().__init__(settings=settings)

        print("PhiModel: ", model_dir)
        print("Settings: ", settings)
        self._model = Llama(model_path=str(model_dir),
                            verbose=False,
                            max_tokens=self._settings.max_tokens,
                            n_gpu_layers=32,
                            n_batch=256,
                            n_threads=256,
                            n_threads_batch=256,
                            n_ctx=32000)

        self._system_prompt_sent = False
        self._stream = True

    def send_message(self, contents: str) -> str:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """

        if self.system_prompt and not self._system_prompt_sent:
            contents = f"{self.system_prompt} {contents}"
            self._system_prompt_sent = True

        self.conversation.add_user_message(contents)
        response = self._model.create_chat_completion(
            messages=self._conversation.construct_api_message(),
            max_tokens=self._settings.max_tokens,  # Limit the length of the output
            temperature=self._settings.temperature,  # Control the creativity of the model (0.0-1.0)
            stream=self._stream,
            # top_p=0.9  # Use nucleus sampling to limit the highest-probability tokens
        )

        if self._stream:
            response_text: str = ''
            for token in response:
                text = token.get('choices', {})[0].get('delta', {}).get('content', '')
                response_text += text
                if self._response_callback:
                    self._response_callback(text)
            if self._response_callback:
                self._response_callback('[END]')
        else:
            response_text = response['choices'][0]['message']['content']

        self.conversation.add_system_message(response_text)

        if not self._stream:
            if self._response_callback:
                self._response_callback(response_text)

        return response_text
