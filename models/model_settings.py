from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    ANTHROPIC = 0
    MISTRAL = 1
    LLAMA = 2
    GEMINI = 3

@dataclass
class ModelSettings:
    model_name: str
    model_id: str
    model_type: ModelType
    max_tokens: int
    temperature: float
    api_key: str
