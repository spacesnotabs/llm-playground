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
    
    # Load both prompts
    linux_op_prompt = load_prompt(yaml_file='prompts.yaml', prompt_name='linux_operator')
    console_analyzer_prompt = load_prompt(yaml_file='prompts.yaml', prompt_name='console_analyzer')
    
    print("Loading Gemini models...")
    
    # Initialize two separate Gemini models with different prompts
    llm_linux = ModelController.create_gemini_model(
        model_name="Gemini",
        api_key=gemini_api
    )
    llm_linux.system_prompt = linux_op_prompt
    llm_linux.initialize()
    
    llm_console = ModelController.create_gemini_model(
        model_name="Gemini",
        api_key=gemini_api
    )
    llm_console.system_prompt = console_analyzer_prompt
    llm_console.initialize()
    
    print("Models loaded. Starting Linux operator...")
    
    # Create and run Linux flow with both LLM instances
    linux_flow = LinuxFlow(llm_linux=llm_linux, llm_console=llm_console)
    
    while True:
        task = input("\nEnter Linux task (or 'exit' to quit): ").strip()
        if task.lower() == 'exit':
            break
            
        linux_flow.run(task)

if __name__ == "__main__":
    main()
