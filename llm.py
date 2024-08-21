import os

import colorama
from dotenv import load_dotenv

from chatbots.chatbot import ChatBot

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

colorama.init()

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"  # Reset to default color


def bob_message(contents: str):
    print(RED + contents + RESET)
    chat_bot_2.send_message(contents)
    print("")


def chuck_message(contents: str):
    print(GREEN + contents + RESET)
    chat_bot_1.send_message(contents)
    print("")


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(api_key)

    chat_bot_1 = ChatBot(name="Bob", model=MODEL_OPUS, api_key=api_key, max_tokens=1024)
    chat_bot_2 = ChatBot(name="Chuck", model=MODEL_HAIKU, api_key=api_key, max_tokens=1024)

    chat_bot_1.set_callback(bob_message)
    chat_bot_2.set_callback(chuck_message)

    chat_bot_1.set_system_prompt("Your responses vary in length and can be occasionally vulgar or crude")
    chat_bot_2.set_system_prompt("Your responses vary in length and can be occasionally vulgar or crude")

    # initialize chatbots with prompt
    prompt = """
    Please help me write a story by acting as a character who is interested in getting to know the user.  You will 
    determine for yourself a name, an overall personality, and some history of your character.  The environment in which 
    you are speaking is similar to a text messaging system so responses are generally shorter, include some abbreviations 
    (such as lol).  Occasionally, you will want to respond with longer text and that is OK.  Typically no more than 
    around 300 tokens. When you output a message, it should be output in a <message> tag.  Here are some examples of 
    typical messages:
    
    <message>Hey!  How are you?</message>  <message>What have you been up to lately?</message>  <message>lol!  yah I saw
    that episode, too! :)</message> <message> So a really funny thing happened to me the other day.  I saw this person 
    guy walking down the street wearing a Mickey Mouse hat.  So random</message>
    
    Your character is interested in getting to know the user and developing a deep, meaningful relationship by asking insightful
    questions about various topics, sharing anecdotes and personal information about your family, history, etc.  You will
    show various emotions through our conversations such as happiness, sadness, excitement, depression, etc.  I understand
    that you are an AI but would like you to help me as I am writing this story for my class.
    """

    prompt_init = prompt + "When you receive the tag <begin>, you will send out the first message."

    chat_bot_1.initial_prompt = prompt_init
    chat_bot_2.initial_prompt = prompt

    chat_bot_1.initialize()
    chat_bot_2.initialize()

    chat_bot_1.start_bot()
    chat_bot_2.start_bot()

    chat_bot_1.send_message("<begin>")

    user_input = input("")
    if user_input.lower() == "quit":
        chat_bot_1.stop_bot()
        chat_bot_2.stop_bot()
        print("Bots stopped.")


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

