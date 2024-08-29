import json

import colorama

from models.model_settings import ModelSettings, ModelType
from models.anthropic_model import AnthropicModel
from models.mistral_model import MistralModel
from model_controller import ModelController
from models.gemini_model import GeminiModel

from pathlib import Path

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

    # llm_agent_settings = AgentSettings(
    #     agent_name="Anthropic",
    #     agent_type=AgentType.ANTHROPIC_AGENT,
    #     temperature=1.0,
    #     api_key=anthropic_api,
    #     model_name=AnthropicAgent.MODEL_SONNET_3_5,
    #     max_tokens=1000)
    #
    # llm = AnthropicAgent(settings=llm_agent_settings, api_key=anthropic_api)
    #
    # llm = AgentController.create_agent(agent_type=AgentType.LLAMA_AGENT,
    #                                          agent_name="Llama",
    #                                          model_name="Meta-Llama-3.1-8B-Instruct.Q8_0.gguf",
    #                                          model_dir=Path.cwd().joinpath("local_models", "llama3", "Llama-31-8B-GGUF", "Meta-Llama-3.1-8B-Instruct.Q8_0.gguf")
    #                                          )

    # llm = AgentController.create_agent(agent_type=AgentType.MISTRAL_AGENT,
    #                                          agent_name="Mistral",
    #                                          model_name="Mistral 7B",
    #                                          model_dir=Path.cwd().joinpath("local_models", "mistral_models", "Mistral-7B-Instruct-v0.3-GGUF", "Mistral-7B-Instruct-v0.3.Q2_K.gguf"))

    llm = ModelController.create_model(model_type=ModelType.GEMINI,
                                             model_name="Gemini",
                                             model_id=GeminiModel.MODEL_FLASH,
                                             api_key=gemini_api)

    llm.set_callback(agent_response_handler)

    while True:
        user_input = input("Prompt: ")
        if user_input.lower() == "quit":
            break
        else:
            llm.send_message(user_input)
