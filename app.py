from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

from agents.base_agent import BaseAgent
from agents.chat_agent import ChatAgent
from agents.coding_agent import CodingAgent
from agents.code_review_agent import CodeReviewAgent
from agents.sw_architect import SWArchitect
from model_controller import ModelController
from models.base_model import BaseModel

app = Flask(__name__)
socketio = SocketIO(app)

# Load model configuration

model_controller = ModelController()
active_model: BaseModel | None = None
active_agent: BaseAgent | None = None

@app.route("/")
def index():
    global active_model
    global active_agent
    active_model = get_model(model_name='gemini', system_prompt='')
    active_agent = get_agent(agent_name='chat', model=active_model)
    return render_template("index.html")


# Model selection and chat clearing
@app.route("/set_model", methods=["POST"])
def set_model():
    global active_model
    selected_model = request.json.get("model")
    active_model = get_model(model_name=selected_model, system_prompt=None)

    return jsonify({"message": "Model set and chat cleared."})


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
    user_input = data.get('message')
    file_path = data.get('file-path')
    print(file_path)
    response = active_agent.run_agent(agent_input={"prompt": user_input})
    # emit('receive_message', {'response': response['response']})


def get_model(model_name: str, system_prompt: str | None):
    global active_model
    model = None
    if model_name == "gemini":
        model = model_controller.get_gemini_model()
    elif model_name == "mistral":
        model = model_controller.get_mistral_model()
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
    return model

def update_chat(text: str):
    print(text)
    print('*')
    socketio.emit('receive_message', {'response': text})
    # socketio.emit('message', text)

def get_agent(agent_name: str, model: BaseModel) -> BaseAgent:
    global active_agent
    agent = None
    if agent_name == "chat":
        agent = ChatAgent(llm=model)
    elif agent_name == "code":
        agent = CodingAgent(llm=model)

    active_agent = agent
    return agent


if __name__ == "__main__":
    socketio.run(app, debug=True)
