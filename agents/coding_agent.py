
from agents.base_agent import BaseAgent
from models.base_model import BaseModel
from tools.file_tools import *


class CodingAgent(BaseAgent):
    input_schema = {
        "type": "object",
        "properties": {
            "prompt": {"type": "string"},
            "path": {"type": "string"},
            "architecture": {"type": "string"}
        },
        "required": ["prompt"]
    }

    output_schema = {
        "type": "object",
        "properties": {
            "response": {"type": "string"},
        },
        "required": ["response"]
    }

    def __init__(self, llm: BaseModel):
        super().__init__(name="Coding Agent", llm=llm)
        self._change_summary = []
        self._last_good_output = {}

    def run_agent(self, agent_input: dict) -> dict:
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        prompt = agent_input["prompt"]
        if agent_input.get("architecture", None):
            architecture = read_file(agent_input["architecture"])
            desc = agent_input["prompt"]
            prompt = f"\nYou are working with code as part of a larger project.  The description of the piece you are working on is '{desc}'. Below is the architecture of the project you are working on which will inform how you write or modify this particular piece:\n" + architecture

        if agent_input.get("path", None):
            if os.path.exists(agent_input["path"]):
                existing_code = read_file(agent_input["path"])
                prompt += f"\nHere is the code to modify: {existing_code}"

        response = self._llm.send_message(prompt)

        agent_output = {"response": response.strip()}

        if not self.validate_output(agent_output=agent_output, schema=self.output_schema):
            return {"error": "Invalid input data."}

        return agent_output
