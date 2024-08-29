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
    def create_model(model_type: ModelType, model_name: str, model_id: str, api_key: str | None = None, model_dir: Path | None = None) -> BaseModel | None:
        model = None
        if model_type == ModelType.ANTHROPIC:
            settings = ModelSettings(
                api_key=api_key,
                model_type=model_type,
                model_name=model_name,
                model_id=model_id,
                max_tokens=500,
                temperature=1.0
            )

            model = AnthropicModel(api_key=api_key, settings=settings)
        elif model_type == ModelType.MISTRAL:
            settings = ModelSettings(
                api_key="",
                model_type=model_type,
                model_name=model_name,
                model_id=model_id,
                max_tokens=2000,
                temperature=1.0
            )
            model = MistralModel(model_dir=model_dir, settings=settings)
        elif model_type == ModelType.LLAMA:
            settings = ModelSettings(
                api_key="",
                model_type=model_type,
                model_name=model_name,
                model_id=model_id,
                max_tokens=200,
                temperature=1.0
            )
            model = LlamaModel(model_dir=model_dir, settings=settings)
        elif model_type == ModelType.GEMINI:
            settings = ModelSettings(
                api_key=api_key,
                model_type=model_type,
                model_name=model_name,
                model_id=model_id,
                max_tokens=2000,
                temperature=1.0
            )
            model = GeminiModel(api_key=api_key, settings=settings)
        else:
            print(f"No model of type {model_type} found.")

        return model
