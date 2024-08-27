import json

import colorama

from agents.agent_settings import AgentSettings, AgentType
from agents.anthropic_agent import AnthropicAgent
from agents.mistral_agent import MistralAgent


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


def agent_response_handler(contents: str) -> None:
    print(GREEN + contents + RESET)


if __name__ == "__main__":

    with open("credentials.json") as f:
        config = json.load(f)

    openai_api = config['llm_apis']['openai']['api_key']
    anthropic_api = config['llm_apis']['anthropic']['api_key']
    gemini_api = config['llm_apis']['gemini']['api_key']

    llm_agent_settings = AgentSettings(
        agent_name="Anthropic",
        agent_type=AgentType.ANTHROPIC_AGENT,
        temperature=1.0,
        api_key=anthropic_api,
        model_name=AnthropicAgent.MODEL_SONNET_3_5,
        max_tokens=1000)

    llm_agent = AnthropicAgent(settings=llm_agent_settings, api_key=anthropic_api)

    llm_agent.set_callback(agent_response_handler)

    while True:
        user_input = input("Prompt: ")
        if user_input.lower() == "quit":
            break
        else:
            llm_agent.send_message(user_input)
