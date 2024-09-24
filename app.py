import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

from agents.base_agent import BaseAgent
from agents.chat_agent import ChatAgent
from agents.coding_agent import CodingAgent
from agents.code_review_agent import CodeReviewAgent
from agents.sw_architect import SWArchitect
from workflows.workflow_controller import WorkflowController
from model_controller import ModelController
from models.base_model import BaseModel
from utils.utils import load_prompt

yaml_file = "prompts.yaml"
write_code_prompt = load_prompt(yaml_file=yaml_file, prompt_name='write_code')

app = Flask(__name__)
socketio = SocketIO(app)

# Load model configuration

model_controller = ModelController()
workflow_controller: WorkflowController | None = None
active_model: BaseModel | None = None
active_agent: BaseAgent | None = None


def workflow_handler(input_prompt: str):
    print('workflow_handler input_data: ', input_prompt)
    update_chat(input_prompt)


@app.route("/")
def index():
    global active_model
    global active_agent
    global workflow_controller

    active_model = get_model(model_name='phi', system_prompt='')
    # active_agent = get_agent(agent_name='code', model=active_model)
    active_agent = get_agent(agent_name='chat', model=active_model)
    # workflow_controller = WorkflowController(workflow_handler)
    # workflow_controller.load_workflow('write_code')
    # workflow_controller.set_agent(active_agent)
    return render_template("index.html")


# Model selection and chat clearing
@app.route("/set_model", methods=["POST"])
def set_model():
    global active_model
    selected_model = request.json.get("model")
    # active_model = get_model(model_name=selected_model, system_prompt=write_code_prompt)
    active_model = get_model(model_name=selected_model, system_prompt=None)

    # workflow_controller.execute_workflow()
    return jsonify({"message": "Model set and chat cleared."})

@app.route("/get_directory_contents", methods=["POST"])
def get_directory_contents():
    print("get_directory_contents()")
    directory = request.json.get("directory")
    if not os.path.isdir(directory):
        return jsonify({"error": "Invalid directory path"}), 400

    def build_tree(path):
        tree = {'name': os.path.basename(path), 'type': 'folder', 'path': path, 'children': []}
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        tree['children'].append(build_tree(entry.path))
                    else:
                        tree['children'].append({
                            'name': entry.name,
                            'type': 'file',
                            'path': entry.path
                        })
        except PermissionError:
            # Handle permission errors gracefully
            tree['children'].append({
                'name': 'Permission Denied',
                'type': 'error',
                'path': path
            })
        return tree

    contents = build_tree(directory)
    return jsonify(contents)

# @app.route("/set_agent", methods=["POST"])
# def set_agent():
#     global active_agent
#     selected_agent = request.json.get("agent")
#     active_agent = selected_agent


# File input via text path
# @app.route("/file_input", methods=["POST"])
# def file_input():
#     file_path = request.json.get("file_path")
#     # Handle the file input in your backend as needed
#     return jsonify({"message": f"File {file_path} received."})

# Chat interaction using SocketIO
@socketio.on('send_message')
def handle_message(data):
    print('handle_message(): ', data)
    global workflow_controller
    input_data = {
        "user_input": data.get('user_input'),
        "files_to_modify": data.get('files_to_modify', []),
        "context_files": data.get('context_files', [])
    }

    if workflow_controller:
        workflow_controller.set_user_input(user_input=input_data)
    else:
        response = active_agent.run_agent(agent_input={"user_input": input_data['user_input']})



@socketio.on('clear_history')
def clear_history():
    active_agent.clear_chat()


def get_model(model_name: str, system_prompt: str | None):
    global active_model
    model = None
    update_chat(text=f"Setting model to {model_name}", system=True)
    if model_name == "gemini":
        model = model_controller.get_gemini_model()
    elif model_name == "mistral":
        model = model_controller.get_mistral_model()
    elif model_name == "phi":
        model = model_controller.get_phi_model()
    else:
        print("No model with name ", model_name)
        return

    if system_prompt:
        model.system_prompt = system_prompt

    model.initialize()
    model._response_callback = update_chat
    active_model = model
    if active_agent:
        active_agent._llm = active_model

    model.clear_conversation()
    socketio.emit('model_changed', {'model': model_name})
    return model


# def update_chat(text: str, system: bool = False) -> None:
def update_chat(text: str, system: bool = False) -> None:
    if system:
        socketio.emit('post_message', {'response': text, 'end': False, 'system': True})
    elif text == '[END]':
        socketio.emit('post_message', {'response': text, 'end': True, 'system': False})
    else:
        socketio.emit('post_message', {'response': text, 'end': False, 'system': False})


def get_agent(agent_name: str, model: BaseModel) -> BaseAgent:
    global active_agent
    agent = None
    if agent_name == "chat":
        agent = ChatAgent(llm=model)
    elif agent_name == "code":
        model.system_prompt = write_code_prompt
        agent = CodingAgent(llm=model)

    active_agent = agent
    return agent


if __name__ == "__main__":
    # socketio.run(app, debug=True, allow_unsafe_werkzeug=True, use_reloader=False)
    socketio.run(app, debug=True)
