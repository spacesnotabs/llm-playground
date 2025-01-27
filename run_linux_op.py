import json
from model_controller import ModelController
from flows.linux_flow import LinuxFlow
from utils.utils import load_prompt

def main():
    # Load configuration
    with open("credentials.json") as f:
        config = json.load(f)
    
    # Get API key
    gemini_api = config['llms']['Gemini']['api_key']
    
    # Load linux operator prompt
    linux_op_prompt = load_prompt(yaml_file='prompts.yaml', prompt_name='linux_operator')
    
    print("Loading Gemini model...")
    
    # Initialize Gemini model
    llm_linux_gemini = ModelController.create_gemini_model(
        model_name="Gemini",
        api_key=gemini_api
    )
    llm_linux_gemini.system_prompt = linux_op_prompt
    llm_linux_gemini.initialize()
    
    print("Model loaded. Starting Linux operator...")
    
    # Create and run Linux flow
    linux_flow = LinuxFlow(llm=llm_linux_gemini)
    
    while True:
        task = input("\nEnter Linux task (or 'exit' to quit): ").strip()
        if task.lower() == 'exit':
            break
            
        linux_flow.run(task)

if __name__ == "__main__":
    main()
