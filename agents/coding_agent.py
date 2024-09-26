from agents.base_agent import BaseAgent
from models.base_model import BaseModel
from tools.file_tools import *
from utils.utils import extract_content


class CodingAgent(BaseAgent):
    """
    Agent for modifying code based on user input.
    """
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
            "diff": {"type": "string"},
            "agent_summary": {"type": "string"},
        },
        "required": ["modified_code", "agent_summary"]
    }

    def __init__(self, llm: BaseModel):
        """
        Initializes the CodingAgent.

        Args:
            llm (BaseModel): The language model to use for code generation.
        """
        super().__init__(name="Coding Agent", llm=llm)
        self._change_summary = []
        self._last_good_output = {}

    def run_agent(self, agent_input: dict) -> dict:
        """
        Runs the agent to modify code based on user input.

        Args:
            agent_input (dict): The input data for the agent.

        Returns:
            dict: The output of the agent, including the modified code, diff, and agent summary.
        """
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        prompt = ""

        # Add context data to the prompt
        if agent_input.get("context", None):
            prompt += f"<context>{agent_input['context'].strip()}</context>"

        # Add architecture if available
        if agent_input.get("architecture", None):
            architecture = read_file(agent_input["architecture"])
            description = agent_input.get("prompt", "")
            prompt += f"You are working with code as part of a larger project.  The description of the piece you are working on is '{description}'."
            prompt += "Below is the architecture of the project in which you are working."
            prompt += f"<architecture>{architecture}</architecture>"

        # Add existing source code if available
        if agent_input.get('code_to_modify', None):
            prompt += f"Here is the code to modify: <code>{agent_input['code_to_modify'].strip()}</code>"

        # Finally, add the user's request
        prompt += agent_input["user_input"].strip()

        modified_code = self._llm.send_message(prompt)
        modified_code = extract_content(modified_code)
        agent_summary = self._llm.send_message("Please provide a summary of the changes you made.")

        diff = ''
        if agent_input.get('code_to_modify', None):
            diff = get_diff(text1=agent_input['code_to_modify'], text2=modified_code)

        agent_output = {"modified_code": modified_code, "diff": diff, "agent_summary": agent_summary}

        if not self.validate_output(agent_output=agent_output, schema=self.output_schema):
            return {"error": "Invalid input data."}

        return agent_output
