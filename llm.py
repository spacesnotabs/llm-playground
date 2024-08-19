from dataclasses import dataclass
from platform import system
from threading import Thread

from dotenv import load_dotenv
from anthropic import Anthropic
import os
import json
import time

from datetime import datetime

USER_ROLE = "user"
ASSIST_ROLE = "assistant"

MODEL_HAIKU = "claude-3-haiku-20240307"
MODEL_SONNET = "claude-3-sonnet-20240229"
MODEL_SONNET_3_5 = "claude-3-5-sonnet-20240620"
MODEL_OPUS = "claude-3-opus-20240229"


def tool_email(contents: str) -> None:
    print("Email sent: ", contents)


email_tool = {
    "name": "email",
    "description": "Sends an email with the contents",
    "input_schema": {
        "type": "object",
        "properties": {
            "contents": {
                "type": "string",
                "description": "The contents of the email"
            }
        },
        "required": ["contents"]
    }
}


@dataclass
class Message:
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class Conversation:
    def __init__(self):

        self._history: list[Message] = []
        self._system_prompt: str | None = None
        self._num_words: int = 0
        self._num_tokens: int = 0

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    @property
    def num_words(self) -> int:
        return self._num_words

    @num_words.setter
    def num_words(self, count: int) -> None:
        self._num_words = count

    @property
    def num_tokens(self) -> int:
        return self._num_tokens

    @num_tokens.setter
    def num_tokens(self, count: int) -> None:
        self._num_tokens = count

    def add_user_message(self, content: str):
        msg = Message(USER_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def add_assistant_message(self, content: str):
        msg = Message(ASSIST_ROLE, content)
        self.num_words += len(content.split())
        self._history.append(msg)

    def construct_api_message(self) -> list:
        return [msg.to_dict() for msg in self._history]

    def save_conversation(self, desc: str) -> None:
        current_datetime = datetime.now()
        filename = current_datetime.strftime(f"conversations/{desc}_%Y%m%d_%H%M%S") + ".txt"
        with open(filename, 'w') as output_file:
            for message in self._history:
                output_file.write(json.dumps(message.to_dict()))


class ChatBot:
    def __init__(self, name: str, api_key: str, model: str, max_tokens: int):
        self._name: str = name
        self._conversation: Conversation | None = None
        self._client = Anthropic(api_key=api_key)
        self._run_thread: Thread | None = None
        self._stop: bool = False
        self._input_message: str | None = None
        self._model: str  = model
        self._max_tokens: int = max_tokens
        self._response_callback = None
        self._create_conversation()
        self._system_prompt = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def conversation(self) -> Conversation:
        return self._conversation

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

    def set_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    def set_callback(self, func) -> None:
        print("Setting response callback ", self._response_callback)
        self._response_callback = func

    def send_message(self, contents: str) -> None:
        self._input_message = contents

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
                    self.conversation.add_user_message(self._input_message)

                response = self._client.messages.create(model=self._model,
                                                  max_tokens=self._max_tokens,
                                                  system=self._system_prompt if self._system_prompt else "",
                                                  messages=self._conversation.construct_api_message(),
                                                  temperature=1
                                                  )

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

    def _create_conversation(self) -> None:
        self.conversation = Conversation()

# def chat_bot(client: Anthropic, num_tokens: int = 500, model: str = MODEL_SONNET_3_5,
#              system_prompt: str | None = None):
#     if not client:
#         return
#
#     convo = Conversation()
#     convo.system_prompt = system_prompt
#
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() == "quit":
#             print("Total tokens: ", convo.num_tokens)
#             print("Total words: ", convo.num_words)
#             convo.save_conversation()
#             return
#
#         convo.add_user_message(user_input)
#
#         use_stream = False
#         # call the model using system prompt if supplied
#         response = client.messages.create(model=model,
#                                           max_tokens=num_tokens,
#                                           system=convo.system_prompt if convo.system_prompt else "",
#                                           messages=convo.construct_api_message(),
#                                           stream=use_stream,
#                                           tools=[email_tool])
#
#         print("Claude: ", end="", flush=True)
#         response_text = ""
#
#         if use_stream:
#             for event in response:
#                 if event.type == "message_start":
#                     convo.num_tokens += event.message.usage.input_tokens
#
#                 elif event.type == "content_block_delta":
#                     print(event.delta.text, flush=True, end="")
#                     response_text += event.delta.text
#
#                 elif event.type == "message_delta":
#                     convo.num_tokens += event.usage.output_tokens
#
#             convo.add_assistant_message(response_text)
#
#             print("\n")
#         else:
#             if response.stop_reason == "tool_use":
#                 tool_use = response.content[-1]
#                 tool_name = tool_use.name
#                 tool_input = tool_use.input
#
#                 if tool_name == "email":
#                     tool_email(tool_input["contents"])
#             elif response.stop_reason == "end_turn":
#                 response_text = response.content[0].text
#                 print("claude: ", response_text)
#                 convo.num_tokens += response.usage.input_tokens
#                 convo.num_tokens += response.usage.output_tokens
#                 convo.add_assistant_message(response_text)

chat_bot_1 = ChatBot(name="Bob", model=MODEL_SONNET_3_5, api_key=api_key, max_tokens=1024)
chat_bot_2 = ChatBot(name="Chuck", model=MODEL_SONNET_3_5, api_key=api_key, max_tokens=1024)

import colorama
colorama.init()

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"  # Reset to default color

def bob_message(contents: str):
    print(RED + "Bob: " + contents + RESET)
    chat_bot_2.send_message(contents)
    print("")

def chuck_message(contents: str):
    print(GREEN + "Chuck: " + contents + RESET)
    chat_bot_1.send_message(contents)
    print("")

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(api_key)

    chat_bot_1.set_callback(bob_message)
    chat_bot_2.set_callback(chuck_message)

    chat_bot_1.set_prompt("Your name is Bob. You are open and honest, though occasionally vulgar.")
    chat_bot_2.set_prompt("Your name is Chuck. You are open and honest, not easily offended.")

    chat_bot_1.start_bot()
    chat_bot_2.start_bot()

    chat_bot_1.send_message("You and I are humans having a very natural conversation, getting to know each other.  Our responses are succint, as though we're engaged in a text message discussion, but meaningful.  We are open and honest as we discuss anything that's on our minds, no matter how random or emotional.")

    user_input = input("")
    if user_input.lower() == "quit":
        chat_bot_1.stop_bot()
        chat_bot_2.stop_bot()
        print("Bots stopped.")