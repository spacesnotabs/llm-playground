from pathlib import Path

from models.anthropic_model import AnthropicModel, BaseModel
from models.mistral_model import MistralModel
from models.llama_model import LlamaModel
from models.gemini_model import GeminiModel
from models.model_settings import ModelType, ModelSettings


class ModelController:
    def __init__(self):
        self._agents: list[BaseModel] = []

    @staticmethod
    def create_anthropic_model(model_name: str, model_id: str, api_key: str | None = None) -> AnthropicModel | None:
        settings = ModelSettings(
            api_key=api_key,
            model_type=ModelType.ANTHROPIC,
            model_name=model_name,
            model_id=model_id,
            max_tokens=3000,
            temperature=1.0
        )
        return AnthropicModel(api_key=api_key, settings=settings)

    @staticmethod
    def create_mistral_model(model_name: str, model_id: str, model_dir: Path | None = None) -> MistralModel | None:
        settings = ModelSettings(
            api_key="",
            model_type=ModelType.MISTRAL,
            model_name=model_name,
            model_id=model_id,
            max_tokens=32000,
            temperature=0.8
        )
        return MistralModel(model_dir=model_dir, settings=settings)

    @staticmethod
    def create_llama_model(model_name: str, model_id: str, model_dir: Path | None = None) -> LlamaModel | None:
        settings = ModelSettings(
            api_key="",
            model_type=ModelType.LLAMA,
            model_name=model_name,
            model_id=model_id,
            max_tokens=200,
            temperature=1.0
        )
        return LlamaModel(model_dir=model_dir, settings=settings)

    @staticmethod
    def create_gemini_model(model_name: str, api_key: str | None = None, model_id: str = GeminiModel.MODEL_FLASH) -> GeminiModel | None:
        settings = ModelSettings(
            api_key=api_key,
            model_type=ModelType.GEMINI,
            model_name=model_name,
            model_id=model_id,
            max_tokens=3000,
            temperature=1.0
        )
        return GeminiModel(settings=settings)

