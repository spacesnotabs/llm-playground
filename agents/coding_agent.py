from agents.base_agent import BaseAgent
from models.base_model import BaseModel
from tools.file_tools import *
from utils.utils import extract_content


class CodingAgent(BaseAgent):
    input_schema = {
        "type": "object",
        "properties": {
            "user_input": {"type": "string"},
            "context": {"type": "string"},
            "code_to_modify": {"type": "string"},
            "architecture": {"type": "string"}
        },
        "required": ["user_input"]
    }

    output_schema = {
        "type": "object",
        "properties": {
            "modified_code": {"type": "string"},
            "agent_summary": {"type": "string"},
        },
        "required": ["modified_code", "agent_summary"]
    }

    def __init__(self, llm: BaseModel):
        super().__init__(name="Coding Agent", llm=llm)
        self._change_summary = []
        self._last_good_output = {}

    def run_agent(self, agent_input: dict) -> dict:
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        prompt = ""

        # add context data to the prompt
        if agent_input.get("context", None):
            prompt += f"<context>{agent_input['context']}</context>"

        # add architecture if available
        if agent_input.get("architecture", None):
            architecture = read_file(agent_input["architecture"])
            desc = agent_input["prompt"]
            prompt += f"\nYou are working with code as part of a larger project.  The description of the piece you are working on is '{desc}'."
            prompt += "Below is the architecture of the project in which you are working."
            prompt += f"<architecture>{architecture}</architecture>"

        # add existing source code if available
        if agent_input.get('code_to_modify', None):
            prompt += f"\nHere is the code to modify: <code>{agent_input['code_to_modify']}</code>"

        # finally, add the user's request
        prompt += agent_input["user_input"]

        # print("Coding Agent Input Prompt:")
        # print('  ', prompt)

        response = self._llm.send_message(prompt)
        code, summary = extract_content(response)

        modified_code = code.strip() if code else ""
        agent_summary = summary.strip() if summary else "No modifications were made."
        agent_output = {"modified_code": modified_code, "agent_summary": agent_summary}

        if not self.validate_output(agent_output=agent_output, schema=self.output_schema):
            return {"error": "Invalid input data."}

        return agent_output
