import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

from agents.base_agent import BaseAgent
from agents.chat_agent import ChatAgent
from agents.coding_agent import CodingAgent
from workflows.workflow_controller import WorkflowController
from model_controller import ModelController
from models.base_model import BaseModel
from utils.utils import load_prompt

yaml_file = "prompts.yaml"
write_code_prompt = load_prompt(yaml_file=yaml_file, prompt_name='write_code')

app = Flask(__name__)
socketio = SocketIO(app)

# Load model configuration

workflow_controller: WorkflowController | None = None

class ModelManager:
    """
    Manages the different models available in the application.
    """
    def __init__(self):
        self.active_model: BaseModel | None = None
        self.chat_model: BaseModel | None = None
        self.model_controller = ModelController()

    def get_model_names(self) -> list[str]:
        """
        Returns a list of available model names.
        """
        return self.model_controller.available_models

    def get_active_model(self) -> BaseModel | None:
        """
        Returns the currently active model.
        """
        return self.active_model

    def get_chat_model(self) -> BaseModel | None:
        """
        Returns the model currently used for chat.
        """
        return self.chat_model

    def set_active_model(self, model_name: str, system_prompt: str | None = None):
        """
        Sets the active model.
        """
        model = self.model_controller.get_model(model_name)
        if system_prompt:
            model.system_prompt = system_prompt
        # model.set_callback(post_llm_update)
        model.initialize()
        self.active_model = model

    def set_chat_model(self, model_name: str):
        """
        Sets the model used for chat.
        """
        model = self.model_controller.get_model(model_name)
        model.initialize()
        model.set_callback(post_llm_update)
        self.chat_model = model

class AgentManager:
    """
    Manages the different agents available in the application.
    """
    def __init__(self):
        self.active_agent: BaseAgent | None = None

    def get_active_agent(self) -> BaseAgent | None:
        """
        Returns the currently active agent.
        """
        return self.active_agent

    def set_active_agent(self, agent: BaseAgent, model: BaseModel):
        """
        Sets the active agent.
        """
        agent.llm = model
        agent._status_message_callback = post_llm_update
        self.active_agent = agent

model_manager = ModelManager()
agent_manager = AgentManager()

class FileManager:
    """
    Manages files uploaded by the user.
    """
    def __init__(self):
        self.uploaded_files = {}
        self.accessed_files = set()

    def upload_file(self, file_name: str, file_content: str):
        """
        Stores the uploaded file content.
        """
        self.uploaded_files[file_name] = file_content

    def get_file_content(self, file_name: str):
        """
        Retrieves the content of a file.
        """
        if file_name in self.uploaded_files:
            self.accessed_files.add(file_name)
            return self.uploaded_files[file_name]
        else:
            return None

    def is_file_accessed(self, file_name: str):
        """
        Checks if the file content has been accessed.
        """
        return file_name in self.accessed_files

    def get_all_file_content(self) -> str:
        """
        Returns the combined contents of all available files.
        """
        return '\n'.join(self.uploaded_files.values())

    def clear_files(self):
        """
        Clears all uploaded files.
        """
        self.uploaded_files = {}
        self.accessed_files = set()

file_manager = FileManager()

def get_chat_model() -> BaseModel | None:
    """
    Returns the chat model.
    """
    return model_manager.get_chat_model()

def get_active_agent() -> BaseAgent | None:
    """
    Returns the active agent.
    """
    return agent_manager.get_active_agent()

def workflow_handler(input_prompt: str):
    print('WORKFLOW_HANDLER: ', input_prompt)
    """
    Handles input prompts for the workflow.
    """
    post_llm_update(input_prompt)


@app.route("/")
def index():
    """
    Renders the index page.
    """
    global workflow_controller
    # get available LLMs
    model_names = model_manager.get_model_names()
    model_manager.set_chat_model(model_names[0])
    model_manager.set_active_model(model_names[0], system_prompt=write_code_prompt)
    workflow_controller = WorkflowController(input_provider=workflow_handler)
    agent = CodingAgent(llm=model_manager.get_active_model())
    set_workflow_agent(agent=agent)
    return render_template("index.html", model_names=model_names)


# Model selection and chat clearing
@app.route("/set_model", methods=["POST"])
def set_model():
    """
    Sets the selected model and clears the chat history.
    """
    selected_model = request.json.get("model")
    model_manager.set_chat_model(model_name=selected_model)
    model_manager.set_active_model(model_name=selected_model)

    post_system_update(f"Set model to {selected_model}")
    return jsonify({"message": "Model set and chat cleared."})

def build_directory_tree(path: str, exclude_dirs: list[str] = ['__pycache__'], top_level: bool = False) -> dict:
    """
    Builds a directory tree representation.
    """
    if top_level:
        tree = {'name': os.path.abspath(path), 'type': 'folder', 'path': path, 'children': []}
    else:
        tree = {'name': os.path.basename(path), 'type': 'folder', 'path': path, 'children': []}
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir() and not entry.name.startswith('.') and entry.name not in exclude_dirs:
                    tree['children'].append(build_directory_tree(entry.path))
                elif entry.is_file() and not entry.name.endswith(('.txt', '.log')):
                    tree['children'].append({
                        'name': entry.name,
                        'type': 'file',
                        'path': os.path.join(path, entry.name) # Use full path
                    })
    except PermissionError:
        # Handle permission errors gracefully
        tree['children'].append({
            'name': 'Permission Denied',
            'type': 'error',
            'path': path
        })
    return tree

@app.route("/get_directory_contents", methods=["POST"])
def get_directory_contents():
    """
    Returns the contents of a directory.
    """
    directory = request.json.get("directory")
    if not os.path.isdir(directory):
        return jsonify({"error": "Invalid directory path"}), 400

    contents = build_directory_tree(os.path.abspath(directory), top_level=True)
    return jsonify(contents)

# @app.route("/set_agent", methods=["POST"])
# def set_agent():
#     global active_agent
#     selected_agent = request.json.get("agent")
#     active_agent = selected_agent


# Chat interaction using SocketIO
@socketio.on('send_message')
def handle_message(data: dict):
    """
    Handles incoming messages from the client.
    """
    print('handle_message ', data)
    global workflow_controller

    files = []
    if len(data.get('files_to_modify', [])):
        files = [file[:-1] for file in data['files_to_modify'] if file]

    input_data = {
        "user_input": data.get('user_input'),
        "files_to_modify": files,
        "context_files": data.get('context_files', []),
        "content": file_manager.get_all_file_content()
    }

    if workflow_controller.is_running:
        workflow_controller.set_user_input(user_input=input_data)
    else:
        prompt = ''
        # add context files if available
        context = file_manager.get_all_file_content()
        if context:
            print("Appending context")
            prompt += f'<context>{context}</context>'
        prompt += data.get('user_input')
        get_chat_model().send_message(prompt)


@socketio.on('clear_history')
def clear_history():
    """
    Clears the chat history.
    """
    get_active_agent().clear_chat()


def post_system_update(text: str) -> None:
    socketio.emit('post_message', {'response': text, 'end': False, 'system': True, 'user': False})


def post_llm_update(text: str) -> None:
    if '[END]' in text:
        socketio.emit('post_message', {'response': text, 'end': True, 'system': False, 'user': False})
    else:
        socketio.emit('post_message', {'response': text, 'end': False, 'system': False, 'user': False})


# def get_agent(agent_name: str, model: BaseModel) -> BaseAgent:
#     """
#     Returns an agent based on the given name.
#     """
#     agent = None
#     if agent_name == "chat":
#         agent = ChatAgent(llm=model)
#     elif agent_name == "code":
#         model.system_prompt = write_code_prompt
#         agent = CodingAgent(llm=model)
#
#     agent._send_user_message_callback = workflow_handler
#     return agent


def set_workflow_agent(agent: BaseAgent):
    """
    Sets the agent for the workflow.
    """
    if workflow_controller:
        agent_manager.set_active_agent(agent=agent, model=model_manager.get_active_model())
        workflow_controller.set_agent(agent_manager.active_agent)

@socketio.on('start_workflow')
def start_workflow(data: dict):
    """
    Starts the workflow.
    """
    global workflow_controller
    print("Workflow starting")

    selected_model = data['selected_model']

    # TODO add logic here to choose workflow and agents based on input from user
    if workflow_controller:
        post_system_update(text='Starting Workflow')
        model_manager.set_active_model(model_name=selected_model, system_prompt=write_code_prompt)
        agent = agent_manager.get_active_agent()
        agent._status_message_callback = post_llm_update
        workflow_controller.set_agent(agent)
        workflow_controller.load_workflow('code_flow')
        workflow_controller.start_workflow()

@socketio.on('stop_workflow')
def stop_workflow():
    """
    Stops the workflow.
    """
    global workflow_controller
    workflow_controller.exit_workflow()
    post_system_update(text='Stopping Workflow')

@socketio.on('upload_file')
def handle_file_upload(data: dict):
    """
    Handles file uploads from the client.
    """
    # You can now access the file content and name in `data`
    file_content = data.get('fileContent')
    file_name = data.get('fileName')

    file_manager.upload_file(file_name=file_name, file_content=file_content)

    # Emit a response to the client
    emit('file_uploaded', {'message': f'File {file_name} uploaded successfully.'})


if __name__ == "__main__":
    # socketio.run(app, debug=True, allow_unsafe_werkzeug=True, use_reloader=False)
    socketio.run(app, debug=True)
