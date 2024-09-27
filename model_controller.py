from pathlib import Path

from models.anthropic_model import AnthropicModel, BaseModel
from models.mistral_model import MistralModel
from models.llama_model import LlamaModel
from models.gemini_model import GeminiModel
from models.model_settings import ModelType, ModelSettings
import json
import yaml

from models.phi_model import PhiModel


class ModelController:
    """
    A class to manage and retrieve LLM models.
    """
    def __init__(self):
        """
        Initializes the ModelController with an empty list of agents and loads credentials.
        """
        self._agents: list[BaseModel] = []
        self.credentials: dict | None = None
        self._available_models: list[str] | None = None
        self.load_credentials()

    @property
    def available_models(self) -> list[str]:
        """
        Returns a list of models available on this system, based on credentials file
        @return list of available model names
        """
        return self._available_models

    @available_models.setter
    def available_models(self, models: list[str]) -> None:
        self._available_models = models

    @staticmethod
    def create_anthropic_model(model_name: str, model_id: str, api_key: str | None = None) -> AnthropicModel | None:
        """
        Creates an AnthropicModel instance.

        @param model_name: The name of the Anthropic model.
        @param model_id: The ID of the Anthropic model.
        @param api_key: The API key for the Anthropic model.
        @return AnthropicModel instance or None if the API key is not provided.
        """
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
        """
        Creates a MistralModel instance.

        @param model_name: The name of the Mistral model.
        @param model_id: The ID of the Mistral model.
        @param model_dir: The directory containing the Mistral model.
        @return MistralModel instance or None if the model directory is not provided.
        """
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
    def create_phi_model(model_name: str, model_id: str, model_dir: Path | None = None) -> PhiModel | None:
        """
        Creates a PhiModel instance.

        @param model_name: The name of the Phi model.
        @param model_id: The ID of the Phi model.
        @param model_dir: The directory containing the Mistral model.
        @return PhiModel instance or None if the model directory is not provided.
        """
        settings = ModelSettings(
            api_key="",
            model_type=ModelType.PHI,
            model_name=model_name,
            model_id=model_id,
            max_tokens=5000,
            temperature=0.8
        )
        return PhiModel(model_dir=model_dir, settings=settings)

    @staticmethod
    def create_llama_model(model_name: str, model_id: str, model_dir: Path | None = None) -> LlamaModel | None:
        """
        Creates a LlamaModel instance.

        @param model_name: The name of the Llama model.
        @param model_id: The ID of the Llama model.
        @param model_dir: The directory containing the Llama model.
        @return LlamaModel instance or None if the model directory is not provided.
        """
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
        """
        Creates a GeminiModel instance.

        @param model_name: The name of the Gemini model.
        @param api_key: The API key for the Gemini model.
        @param model_id: The ID of the Gemini model.
        @return GeminiModel instance or None if the API key is not provided.
        """
        settings = ModelSettings(
            api_key=api_key,
            model_type=ModelType.GEMINI,
            model_name=model_name,
            model_id=model_id,
            max_tokens=7000,
            temperature=1.0
        )
        return GeminiModel(settings=settings)

    def load_credentials(self):
        """
        Loads credentials from credentials.json
        """
        try:
            with open('credentials.json', 'r') as f:
                self.credentials = json.load(f)
        except FileNotFoundError:
            print("Warning: credentials.json not found. Using default values.")
            self.credentials = {}

        # create list of available models
        if self.credentials:
            self.available_models = [model_name for model_name in self.credentials['llms'].keys()]


    def get_model(self, model_name: str) -> BaseModel | None:
        """
        Retrieves a model instance based on model_name.

        @param model_name: Name of the model to retrieve.
        @return A BaseModel instance or None if the model is not found.
        """
        model = None
        if model_name == "Gemini":
            model = self.get_gemini_model()
        elif model_name == "Mistral":
            model = self.get_mistral_model()
        elif model_name == "Phi":
            model = self.get_phi_model()

        return model

    def get_anthropic_model(self) -> AnthropicModel | None:
        """
        Retrieves an AnthropicModel instance from credentials.

        @return AnthropicModel instance or None if the API key is not found.
        """
        return self.create_anthropic_model(
            model_name='claude-2',
            model_id='claude-2',
            api_key=self.credentials.get('llms', {}).get('Anthropic', {}).get('api_key')
        )

    def get_mistral_model(self) -> MistralModel | None:
        """
        Retrieves a MistralModel instance from credentials.

        @return MistralModel instance or None if the model directory is not found.
        """
        model_dir = Path(self.credentials.get('llms', {}).get('Mistral', {}).get('model_dir', ''),
                         self.credentials.get('model_file', ''))
        return self.create_mistral_model(
            model_name='mistral-7b',
            model_id='mistral-7b',
            model_dir=Path(self.credentials.get('llms', {}).get('mistral', {}).get('model_dir', ''),
                           self.credentials.get('llms', {}).get('mistral', {}).get('model_file', ''))
        )

    def get_phi_model(self) -> PhiModel | None:
        """
        Retrieves a PhiModel instance from credentials.

        @return PhiModel instance or None if the model directory is not found.
        """
        model_dir = Path(self.credentials.get('llms', {}).get('Phi', {}).get('model_dir', ''),
                         self.credentials.get('model_file', ''))
        return self.create_phi_model(
            model_name='phi',
            model_id='phi',
            model_dir=Path(self.credentials.get('llms', {}).get('phi', {}).get('model_dir', ''),
                           self.credentials.get('llms', {}).get('phi', {}).get('model_file', ''))
        )

    def get_llama_model(self) -> LlamaModel | None:
        """
        Retrieves a LlamaModel instance from credentials.

        @return LlamaModel instance or None if the model directory is not found.
        """
        return self.create_llama_model(
            model_name='llama-7b',
            model_id='llama-7b',
            model_dir=Path(self.credentials.get('llms', {}).get('llama', {}).get('model_dir', ''))
        )

    def get_gemini_model(self) -> GeminiModel | None:
        """
        Retrieves a GeminiModel instance from credentials.

        @return GeminiModel instance or None if the API key is not found.
        """
        return self.create_gemini_model(
            model_name='gemini-pro',
            api_key=self.credentials.get('llms', {}).get('Gemini', {}).get('api_key')
        )
