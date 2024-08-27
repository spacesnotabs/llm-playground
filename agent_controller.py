from pathlib import Path

from agents.anthropic_agent import AnthropicAgent, BaseAgent
from agents.mistral_agent import MistralAgent
from agents.llama_agent import LlamaAgent
from agents.agent_settings import AgentType, AgentSettings


class AgentController:
    def __init__(self):
        self._agents: list[BaseAgent] = []

    @staticmethod
    def create_agent(agent_type: AgentType, agent_name: str, model_name: str, api_key: str | None = None, model_dir: Path | None = None) -> BaseAgent | None:
        if agent_type == AgentType.ANTHROPIC_AGENT:
            settings = AgentSettings(
                api_key=api_key,
                agent_type=agent_type,
                agent_name=agent_name,
                model_name=model_name,
                max_tokens=200,
                temperature=1.0
            )

            agent = AnthropicAgent(api_key=api_key, settings=settings)
            return agent
        elif agent_type == AgentType.MISTRAL_AGENT:
            settings = AgentSettings(
                api_key="",
                agent_type=agent_type,
                agent_name=agent_name,
                model_name=model_name,
                max_tokens=200,
                temperature=1.0
            )
            agent = MistralAgent(model_dir=model_dir, settings=settings)
            return agent
        elif agent_type == AgentType.LLAMA_AGENT:
            settings = AgentSettings(
                api_key="",
                agent_type=agent_type,
                agent_name=agent_name,
                model_name=model_name,
                max_tokens=200,
                temperature=1.0
            )
            agent = LlamaAgent(model_dir=model_dir, settings=settings)
            return agent
        else:
            print(f"No agent of type {agent_type} found.")
            return None
