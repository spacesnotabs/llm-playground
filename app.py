import json
from pathlib import Path

from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api
from flask_bootstrap import Bootstrap

from agent_controller import AgentController
from agents.agent_task import AgentTask, TaskType, OutputTarget, ExecType, create_llm_task
from agents.chat_agent import ChatAgent
from agents.coding_agent import CodingAgent
from agents.email_agent import EmailAgent
from agents.task_flow import TaskFlow
from model_controller import ModelController, ModelType
from models.anthropic_model import AnthropicModel
from models.mistral_model import MistralModel
from models.gemini_model import GeminiModel
import yaml

app = Flask(__name__, static_url_path='/static')
api = Api(app)
bootstrap = Bootstrap(app)  # Initialize Bootstrap


@app.route('/')
def index():
    """Render the index.html template."""
    return render_template('index.html', models=models.keys())


# --- Global Variables for Agents and Models ---
agents = {}
models = {}
task_flow = None


# --- Helper Functions ---
def load_credentials():
    """Loads credentials from a JSON file."""
    with open('credentials.json') as f:
        return json.load(f)


def load_prompt(yaml_file: str, prompt_name: str):
    """Loads prompts from a YAML file."""
    with open(yaml_file, 'r') as file:
        prompts = yaml.safe_load(file)

    prompt_data = prompts['prompts'].get(prompt_name, {})

    # Define the order of fields and their corresponding tags
    field_order = [
        ('instruction', 'instruction'),
        ('output_format', 'output_format'),
        ('additional_instructions', 'additional_instructions'),
        ('example_output', 'example'),
        ('final_instruction', 'final_instruction')
    ]

    prompt_parts = []
    for field, tag in field_order:
        if field in prompt_data:
            content = prompt_data[field].strip()
            prompt_parts.append(f"<{tag}>\n{content}\n</{tag}>")

    return "\n\n".join(prompt_parts)


def create_coding_agent(model_name: str) -> (CodingAgent, str):
    """Creates a CodingAgent with the specified model."""
    model = models.get(model_name)
    if not model:
        return None, "Model not found"

    # Load prompts from YAML
    yaml_file = 'prompts.yaml'
    write_code_prompt = load_prompt(yaml_file, 'write_code')
    code_review_prompt = load_prompt(yaml_file, 'code_review')

    # Instantiate the CodingAgent
    agent = CodingAgent(llm_code=model, llm_review=model)
    agent._llm_code.system_prompt = write_code_prompt
    agent._llm_review.system_prompt = code_review_prompt
    agent._llm_code.initialize()
    agent._llm_review.initialize()
    return agent, None


# --- API Resources ---
class ModelsAPI(Resource):
    def get(self):
        """Get a list of available models."""
        return jsonify(list(models.keys()))

    def post(self):
        """Create a new model."""
        data = request.get_json()
        model_type = data.get('model_type')
        model_name = data.get('model_name')
        model_id = data.get('model_id')
        api_key = data.get('api_key')
        model_dir = data.get('model_dir')

        if model_type not in [e.name for e in ModelType]:
            return jsonify({"error": "Invalid model type"}), 400

        model = ModelController.create_model(model_type=ModelType[model_type],
                                             model_name=model_name,
                                             model_id=model_id,
                                             api_key=api_key,
                                             model_dir=Path(model_dir) if model_dir else None)
        if not model:
            return jsonify({"error": "Failed to create model"}), 500

        models[model_name] = model
        return jsonify({"message": "Model created", "model_name": model_name}), 201


class AgentsAPI(Resource):
    def get(self):
        """Get a list of created agents."""
        return jsonify(list(agents.keys()))

    def post(self):
        """Create a new agent."""
        data = request.get_json()
        agent_type = data.get('agent_type')
        agent_name = data.get('agent_name')
        model_name = data.get('model_name')

        if agent_type == 'coding':
            agent, error = create_coding_agent(model_name)
            if error:
                return jsonify({"error": error}), 400

        elif agent_type == 'email':
            model = models.get(model_name)
            if not model:
                return jsonify({"error": "Model not found"}), 400
            agent = EmailAgent(llm=model)

        elif agent_type == 'chat':
            model = models.get(model_name)
            if not model:
                return jsonify({"error": "Model not found"}), 400
            agent = ChatAgent(llm=model)
        else:
            return jsonify({"error": "Invalid agent type"}), 400

        agents[agent_name] = agent
        return jsonify({"message": "Agent created", "agent_name": agent_name}), 201


class AgentTasksAPI(Resource):
    def post(self, agent_name):
        """Create a new task for the specified agent."""
        agent = agents.get(agent_name)
        if not agent:
            return jsonify({"error": "Agent not found"}), 404

        data = request.get_json()
        task_type = data.get('task_type')
        task_prompt = data.get('prompt')
        filepath = data.get('filepath', None)

        # For now, we assume tasks are LLM-based
        task_flow = TaskFlow()
        task_flow.add_agent(agent)
        first_input = {"prompt": task_prompt,
                       "code": "",
                       "filepath": filepath,
                       "projectpath": ""}

        if filepath:
            # If a filepath is provided, add a read_file task
            read_task = create_llm_task(input_data=first_input, task_id="read_file")
            task_flow.add_task(read_task)
        else:
            first_input["filepath"] = "output_code.py"

        # Add a code modification task
        code_task = create_llm_task(input_data=first_input, task_id="code")
        task_flow.add_task(code_task)

        agent_controller = AgentController()
        agent_controller.task_flow = task_flow
        results = agent_controller.run_task_flow()  # Run the task flow synchronously for now

        return jsonify({"message": "Task executed", "results": results}), 200

    # class AgentTaskFlowAPI(Resource):
    #
    #     def post(self):

    # --- Add API Resources ---

class CodeAgentAPI(Resource):
    def post(self, agent_type):
        """Run a code agent."""
        if agent_type not in ['code_writer', 'code_modifier']:
            return jsonify({"error": "Invalid agent type"}), 400

        data = request.get_json()
        agent = ChatAgent(llm=models['mistral'])  # Get the relevant model

        output = agent.run_agent(data)
        return jsonify(output), 200

chat_agent: ChatAgent | None = None
class ChatAgentAPI(Resource):
    def post(self, agent_type):
        global chat_agent
        if agent_type not in ['chat_agent'] :
           return jsonify({"error": "Invalid agent type"}), 400

        if not chat_agent:
            chat_agent = ChatAgent(llm=models['Mistral'])

        data = request.get_json()
        output = chat_agent.run_agent(data)
        return output, 200

    def clear_chat(self):
        global chat_agent
        if not chat_agent:
            return jsonify({"error": "No chat agent active"}), 400

        output = chat_agent.clear_chat()
        return output, 200

api.add_resource(CodeAgentAPI, '/agents/code/<string:agent_type>')
api.add_resource(ChatAgentAPI, '/agents/chat/<string:agent_type>')

api.add_resource(ModelsAPI, '/models')
api.add_resource(AgentsAPI, '/agents')
api.add_resource(AgentTasksAPI, '/agents/<string:agent_name>/tasks')

chat_api_instance = ChatAgentAPI()

# add custom routs
app.add_url_rule('/agents/chat/clear', view_func=chat_api_instance.clear_chat, methods=['POST'])

if __name__ == '__main__':
    credentials = load_credentials()
    gemini_api = credentials['llm_apis']['gemini']['api_key']
    # ... (Load your default models here based on credentials, like in llm.py)
    llm_write_code = ModelController.create_model(model_type=ModelType.GEMINI,
                                                  model_name="Gemini",
                                                  model_id=GeminiModel.MODEL_FLASH,
                                                  api_key=gemini_api)

    llm_review_code = ModelController.create_model(model_type=ModelType.GEMINI,
                                                   model_name="Gemini",
                                                   model_id=GeminiModel.MODEL_FLASH,
                                                   api_key=gemini_api)

    llm_chat = ModelController.create_model(model_type=ModelType.MISTRAL,
                                            model_name="Mistral",
                                            model_id="Mistral 7B",
                                            model_dir=Path.cwd().joinpath("local_models", "mistral_models",
                                                                          "Mistral-7B-Instruct-v0.3-GGUF",
                                                                          "Mistral-7B-Instruct-v0.3.Q2_K.gguf"))

    models[llm_write_code.model_name] = llm_write_code
    models[llm_review_code.model_name] = llm_review_code
    models[llm_chat.model_name] = llm_chat

    app.run(debug=True)
