from agents.base_agent import BaseAgent
from models.base_model import BaseModel

class ChatAgent(BaseAgent):
    input_schema = {
        "type": "object",
        "properties": {
            "user_input": {"type": "string"}
        },
        "required": ["user_input"]
    }

    output_schema = {
        "type": "object",
        "properties": {
            "response": {"type": "string"}
        },
        "required": ["response"]
    }

    def __init__(self, llm: BaseModel):
        super().__init__(name="Chat Agent", llm=llm)

    def run_agent(self, agent_input: dict) -> dict:
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        response = self._llm.send_message(agent_input["user_input"])
        agent_output = {"response": response}

        if not self.validate_output(agent_output=agent_output, schema=self.output_schema):
            return {"error": "Invalid input data."}

        return {"response": response}

    def clear_chat(self) -> dict:
        if self._llm:
            self._llm.clear_conversation()

        return {"response": "Cleared chat history"}
