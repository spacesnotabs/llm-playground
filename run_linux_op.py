import json
from models.model_controller import ModelController
from flows.linux_flow import LinuxFlow
from utils.utils import load_prompt
import argparse

def run_interactive_mode(linux_flow):
    """Run the Linux operator in interactive mode."""
    print("\nEntering interactive mode (type 'exit' to quit)")
    while True:
        task = input("\nEnter Linux task (or 'exit' to quit): ").strip()
        if task.lower() == 'exit':
            break
        linux_flow.run(task)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Linux Operation Assistant')
    parser.add_argument('-t', '--task', help='Linux task to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()

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
    
    if args.task:
        # Execute single task mode
        linux_flow.run(args.task)
    else:
        # Run interactive mode if no task provided or -i flag is set
        run_interactive_mode(linux_flow)

if __name__ == "__main__":
    main()
