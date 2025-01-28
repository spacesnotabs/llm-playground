from agents.base_agent import BaseAgent
from models.base_model import BaseModel
from utils.utils import extract_content


class LinuxOpAgent(BaseAgent):
    """
    Agent for generating and managing Linux shell commands based on user requirements.
    """
    input_schema = {
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "error_feedback": {"type": ["string", "null"], "default": None}
        },
        "required": ["task"]
    }

    output_schema = {
        "type": "object",
        "properties": {
            "commands": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "purpose": {"type": "string"}
                    },
                    "required": ["command", "purpose"]
                }
            },
            "error_handling": {
                "type": "object",
                "properties": {
                    "previous_error": {"type": ["string", "null"]},
                    "resolution": {"type": ["string", "null"]}
                },
                "required": ["previous_error", "resolution"]
            }
        },
        "required": ["commands", "error_handling"]
    }

    def __init__(self, llm: BaseModel):
        """
        Initializes the LinuxOpAgent.

        Args:
            llm (BaseModel): The language model to use for command generation.
        """
        super().__init__(name="Linux Operator Agent", llm=llm)

    def run_agent(self, agent_input: dict) -> dict:
        """
        Runs the agent to generate Linux commands based on user requirements.

        Args:
            agent_input (dict): The input data containing the task and optional error feedback.

        Returns:
            dict: Generated commands and error handling information.
        """
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        prompt = "Generate Linux commands for the following task:\n"
        prompt += f"Task: {agent_input['task'].strip()}\n"

        if agent_input.get("error_feedback"):
            prompt += f"Previous Error: {agent_input['error_feedback'].strip()}\n"
            prompt += "Please provide updated commands that address this error."

        self.post_message(message="Generating Linux commands...")
        response = self.llm.send_message(prompt)
        response = extract_content(response)

        try:
            # Convert string response to dictionary if needed
            if isinstance(response, str):
                import json
                response = json.loads(response)

            if not self.validate_output(agent_output=response, schema=self.output_schema):
                return {"error": "Invalid output format from LLM."}

            return response

        except Exception as e:
            return {"error": f"Failed to process LLM response: {str(e)}"}
