import json
from pathlib import Path

import tools.file_tools
from agents.chat_agent import ChatAgent
from agents.code_review_agent import CodeReviewAgent
from agents.sw_architect import SWArchitect
from agents.coding_agent import CodingAgent
from model_controller import ModelController
from utils.utils import extract_content, load_prompt
from workflows.workflow_controller import WorkflowController

def user_input(inputs: list, outputs: list) -> dict:
    output_data: dict = {}
    print('user-input: ', inputs)
    print('user-input: ', outputs)
    for item in outputs:
        output_data[item] = input(inputs[item])

    return output_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["build_app_mode", "chat_mode", "code_mode", "workflow_mode"], required=True)
    args = parser.parse_args()
    
    with open("credentials.json") as f:
        config = json.load(f)

    # Usage example

    openai_api = config['llms']['openai']['api_key']
    anthropic_api = config['llms']['anthropic']['api_key']
    gemini_api = config['llms']['gemini']['api_key']

    yaml_file = 'prompts.yaml'
    write_code_prompt = load_prompt(yaml_file=yaml_file, prompt_name='write_code')
    review_code_prompt = load_prompt(yaml_file=yaml_file, prompt_name="code_review")
    sw_arch_prompt = load_prompt(yaml_file=yaml_file, prompt_name="sw_architect")

    print("Loading models...")

    """
    Gemini Code Review LLM 
    """
    llm_review_code_gemini = ModelController.create_gemini_model( model_name="Gemini", api_key=gemini_api)
    llm_review_code_gemini.system_prompt = review_code_prompt
    llm_review_code_gemini.initialize()

    """
    Gemini Chat Mode LLM
    """
    llm_chat_gemini = ModelController.create_gemini_model(model_name="Gemini", api_key=gemini_api)
    llm_chat_gemini.initialize()

    """
    Gemini Write Code LLM
    """
    llm_write_code_gemini = ModelController.create_gemini_model(model_name="Gemini", api_key=gemini_api)
    llm_write_code_gemini.system_prompt = write_code_prompt
    llm_write_code_gemini.initialize()

    """
    Gemini SW Architecture LLM
    """
    llm_swarch_gemini = ModelController.create_gemini_model(model_name="Gemini", api_key=gemini_api)
    llm_swarch_gemini.system_prompt = sw_arch_prompt
    llm_swarch_gemini.initialize()

    """
    Phi Chat
    """
    # llm_chat_phi = ModelController.create_phi_model(model_name="Phi", )
    """
    Mistral Code Writing LLM 
    """
    # llm_write_code_mistral = ModelController.create_mistral_model(model_name="Mistral",
    #                                                       model_id="Mistral 7B",
    #                                                       model_dir=Path.cwd().joinpath("local_models",
    #                                                                                     "mistral_models",
    #                                                                                     "Mistral-7B-Instruct-v0.3-GGUF",
    #                                                                                     "Mistral-7B-Instruct-v0.3.Q2_K.gguf"))
    # llm_write_code_mistral.system_prompt = write_code_prompt
    # llm_write_code_mistral.initialize()

    print("Models loaded.")

    sw_arch_agent = SWArchitect(llm=llm_swarch_gemini)
    code_agent = CodingAgent(llm=llm_write_code_gemini)
    review_agent = CodeReviewAgent(llm=llm_review_code_gemini)
    chat_agent = ChatAgent(llm=llm_chat_gemini)

    if args.mode == "build_app_mode":
        app_prompt: str = input("App to write: ")
        response = sw_arch_agent.run_agent(agent_input={"prompt": app_prompt.strip()})

        for file in response['response']['file_structure']:
            filepath = file["path"]
            prompt = {"prompt": file["description"], "architecture": "architecture.txt", "path": filepath}

            # write code for this file
            response = code_agent.run_agent(agent_input=prompt)
            code_output = extract_content(response["response"].strip(), "CODE")

            # write the code to the specified file
            tools.file_tools.write_file(filename=filepath, content=code_output)
            code_agent.clear_chat()

            # review the code
            prompt = {"prompt": "", "architecture": "architecture.txt", "path": filepath}
            review_output = review_agent.run_agent(agent_input=prompt)

            # provide feedback and write the updated code back to the file
            coding_prompt = f"Please make the following changes to the code: {review_output['response']}"
            prompt = {"prompt": coding_prompt, "path": filepath}
            response = code_agent.run_agent(agent_input=prompt)
            code_output = extract_content(response["response"].strip(), "CODE")
            summary_output = extract_content(response["response"].strip(), "SUMMARY")
            tools.file_tools.write_file(filename=file["path"], content=code_output)
            print(summary_output)

            # cleanup
            code_agent.clear_chat()
            review_agent.clear_chat()

    elif args.mode == "code_mode":
        filepath = input("What file should I modify? ").strip()
        context= input("Any other files to use as context? ")
        instructions = input("What's your objective? ").strip()

        prompt = {"prompt": instructions.strip(), "path": filepath}

        if context != "":
            context_files = [filepath for filepath in context.split(',')]
            prompt["context-files"] = context_files

        response = code_agent.run_agent(agent_input=prompt)

        code_output = extract_content(response["response"].strip(), "CODE")
        if code_output:
            tools.file_tools.write_file(filename=filepath, content=code_output)
        else:
            print("No code output found...")
            exit()

        summary_output = extract_content(response["response"].strip(), "SUMMARY")
        if summary_output:
            print("Summary output found: ", summary_output)
        else:
            print("No summary found...")

    elif args.mode == "chat_mode":
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            response = chat_agent.run_agent(agent_input={"prompt": user_input})
            print(f"ChatAgent: {response['response']}")
    elif args.mode == "workflow_mode":
        controller = WorkflowController(user_input)
        # controller.load_workflow('write_code')
        # controller.set_agent(code_agent)
        controller.load_workflow('chat')
        controller.set_agent(chat_agent)
        controller.execute_workflow()
    else:
        print("Invalid mode specified.")
