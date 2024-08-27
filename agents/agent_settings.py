from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    ANTHROPIC_AGENT = 0
    MISTRAL_AGENT = 1
    LLAMA_AGENT = 2

@dataclass
class AgentSettings:
    agent_name: str
    model_name: str
    agent_type: AgentType
    max_tokens: int
    temperature: float
    api_key: str
