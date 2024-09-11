from anthropic import Anthropic
from anthropic.types import ToolUseBlock

from .base_model import BaseModel
from .model_settings import ModelSettings
from tools.file_tools import process_tool_call


class AnthropicModel(BaseModel):
    MODEL_HAIKU = "claude-3-haiku-20240307"
    MODEL_SONNET = "claude-3-sonnet-20240229"
    MODEL_SONNET_3_5 = "claude-3-5-sonnet-20240620"
    MODEL_OPUS = "claude-3-opus-20240229"

    def __init__(self, api_key: str, settings: ModelSettings):
        super().__init__(settings=settings)
        self._client = Anthropic(api_key=api_key)

    def send_message(self, contents: str) -> None:
        """
        Send a prompt to the API and return the response
        :param prompt: the prompt to send
        :return: the response
        """
        self.conversation.add_user_message(contents)

        response = self._client.messages.create(model=self._settings.model_id,
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

        elif response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input
            tool_result = process_tool_call(tool_name, tool_input)

            convo_history = self.conversation.construct_api_message()
            llm_response = {
                "role": "assistant",
                "content": response.content
            }

            convo_history.append(llm_response)
            print("tool_meassage: ", llm_response)
            convo_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": tool_result
                    }
                ]
            })

            tool_response = self._client.messages.create(model=self._settings.model_id,
                                                         max_tokens=self._settings.max_tokens,
                                                         system=self._system_prompt if self._system_prompt else "",
                                                         messages=convo_history,
                                                         temperature=self._settings.temperature,
                                                         top_k=500
                                                         )

            if not isinstance(tool_response.content[0], ToolUseBlock):
                self.conversation.add_assistant_message(tool_response.content[0].text)

                if self._response_callback:
                    self._response_callback(tool_response.content[0].text)
