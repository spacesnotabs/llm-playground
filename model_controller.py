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
        self.load_credentials()

    def available_models(self) -> list[str]:
        """
        Returns a list of models available on this system, based on credentials file
        @return list of available model names
        """
        models: list[str] = []
        if self.credentials:
            models = [model_name for model_name in self.credentials['llms'].keys()]

        return models

    @staticmethod
    def create_anthropic_model(model_name: str, model_id: str, api_key: str | None = None) -> AnthropicModel | None:
        """
        Creates an AnthropicModel instance.

        Args:
            model_name (str): The name of the Anthropic model.
            model_id (str): The ID of the Anthropic model.
            api_key (str, optional): The API key for the Anthropic model. Defaults to None.

        Returns:
            AnthropicModel | None: An AnthropicModel instance or None if the API key is not provided.
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

        Args:
            model_name (str): The name of the Mistral model.
            model_id (str): The ID of the Mistral model.
            model_dir (Path, optional): The directory containing the Mistral model. Defaults to None.

        Returns:
            MistralModel | None: A MistralModel instance or None if the model directory is not provided.
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

        Args:
            model_name (str): The name of the Phi model.
            model_id (str): The ID of the Phi model.
            model_dir (Path, optional): The directory containing the Mistral model. Defaults to None.

        Returns:
            PhiModel | None: A PhiModel instance or None if the model directory is not provided.
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

        Args:
            model_name (str): The name of the Llama model.
            model_id (str): The ID of the Llama model.
            model_dir (Path, optional): The directory containing the Llama model. Defaults to None.

        Returns:
            LlamaModel | None: A LlamaModel instance or None if the model directory is not provided.
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

        Args:
            model_name (str): The name of the Gemini model.
            api_key (str, optional): The API key for the Gemini model. Defaults to None.
            model_id (str, optional): The ID of the Gemini model. Defaults to GeminiModel.MODEL_FLASH.

        Returns:
            GeminiModel | None: A GeminiModel instance or None if the API key is not provided.
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

    def get_anthropic_model(self) -> AnthropicModel | None:
        """
        Retrieves an AnthropicModel instance from credentials.

        Returns:
            AnthropicModel | None: An AnthropicModel instance or None if the API key is not found.
        """
        return self.create_anthropic_model(
            model_name='claude-2',
            model_id='claude-2',
            api_key=self.credentials.get('llms', {}).get('anthropic', {}).get('api_key')
        )

    def get_mistral_model(self) -> MistralModel | None:
        """
        Retrieves a MistralModel instance from credentials.

        Returns:
            MistralModel | None: A MistralModel instance or None if the model directory is not found.
        """
        model_dir = Path(self.credentials.get('llms', {}).get('mistral', {}).get('model_dir', ''),
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

        Returns:
            PhiModel | None: A PhiModel instance or None if the model directory is not found.
        """
        model_dir = Path(self.credentials.get('llms', {}).get('phi', {}).get('model_dir', ''),
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

        Returns:
            LlamaModel | None: A LlamaModel instance or None if the model directory is not found.
        """
        return self.create_llama_model(
            model_name='llama-7b',
            model_id='llama-7b',
            model_dir=Path(self.credentials.get('llms', {}).get('llama', {}).get('model_dir', ''))
        )

    def get_gemini_model(self) -> GeminiModel | None:
        """
        Retrieves a GeminiModel instance from credentials.

        Returns:
            GeminiModel | None: A GeminiModel instance or None if the API key is not found.
        """
        return self.create_gemini_model(
            model_name='gemini-pro',
            api_key=self.credentials.get('llms', {}).get('gemini', {}).get('api_key')
        )
