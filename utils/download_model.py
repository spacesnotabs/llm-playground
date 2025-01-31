from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
from pathlib import Path

def download_llama():
    print("Downloading llama models")
    # Specify the model name
    model_name = "neuralmagic/Meta-Llama-3.1-70B-Instruct-quantized.w4a16"

    # Load the model and tokenizer
    print("tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("model")
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # (Optional) Save the model locally if you want to keep a local copy
    print("saving model")
    model.save_pretrained("./local_models/llama3")

    print("saving tokenizer")
    tokenizer.save_pretrained("./local_models/llama3")

def download_mistral():
    print("Downloading mistral models")
    mistral_models_path = Path.home().joinpath('local_models', 'mistral_models', '7B-Instruct-v0.3')
    mistral_models_path.mkdir(parents=True, exist_ok=True)

    snapshot_download(repo_id="mistralai/Mistral-7B-Instruct-v0.3", allow_patterns=["params.json", "consolidated.safetensors", "tokenizer.model.v3"], local_dir=mistral_models_path)

def download_mistral_7b_instruct_03_guff():

    local_dir = Path.cwd().joinpath('local_models', 'mistral_models', 'Mistral-7B-Instruct-v0.3-GGUF')
    local_dir.mkdir(parents=True, exist_ok=True)

    # Specify the model repository ID
    model_repo = "MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF"

    # Download the model
    local_dir = snapshot_download(repo_id=model_repo)

    print(f"Model downloaded to: {local_dir}")

def download_from_hugging_face(repo: str, path: Path):
    path.mkdir(parents=True, exist_ok=True)

    dir = snapshot_download(repo_id=repo)
    print(f"Model downloaded to: {dir}")

if __name__ == "__main__":
    path = Path.cwd().joinpath('local_models', 'llama3', 'Llama-31-70B-quantized')
    # download_from_hugging_face(repo="neuralmagic/Meta-Llama-3.1-70B-Instruct-quantized.w4a16", path=path)
    download_llama()