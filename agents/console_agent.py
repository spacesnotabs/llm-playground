from agents.base_agent import BaseAgent
from models.base_model import BaseModel
from utils.utils import extract_content


class ConsoleAgent(BaseAgent):
    """
    Agent for analyzing console output and providing solutions.
    """
    input_schema = {
        "type": "object",
        "properties": {
            "console_output": {"type": "string"},
            "context": {"type": "string"}
        },
        "required": ["console_output"]
    }

    output_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["error", "warning", "success"]},
            "summary": {"type": "string"},
            "solution": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["command", "explanation"]},
                    "content": {"type": "string"}
                },
                "required": ["type", "content"]
            }
        },
        "required": ["status", "summary", "solution"]
    }

    def __init__(self, llm: BaseModel):
        """
        Initializes the ConsoleAgent.

        Args:
            llm (BaseModel): The language model to use for analysis.
        """
        super().__init__(name="Console Agent", llm=llm)

    def run_agent(self, agent_input: dict) -> dict:
        """
        Runs the agent to analyze console output and provide solutions.

        Args:
            agent_input (dict): The input data containing console output.

        Returns:
            dict: Analysis results including status, summary, and solution.
        """
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        prompt = "Please analyze this console output and provide appropriate solution:\n"

        # Add context if available
        if agent_input.get("context", None):
            prompt += f"Context: {agent_input['context'].strip()}\n"

        # Add console output
        prompt += f"Console Output:\n{agent_input['console_output'].strip()}"

        self.post_message(message="Analyzing console output...")
        analysis = self.llm.send_message(prompt)
        analysis = extract_content(analysis)

        print("Analysis from console_agent: ", analysis)
        try:
            # Convert string response to dictionary if needed
            if isinstance(analysis, str):
                import json
                analysis = json.loads(analysis)

            if not self.validate_output(agent_output=analysis, schema=self.output_schema):
                return {"error": "Invalid output format from LLM."}

            return analysis

        except Exception as e:
            return {"error": f"Failed to process LLM response: {str(e)}"}
