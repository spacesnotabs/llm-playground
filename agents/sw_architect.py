import json

from agents.base_agent import BaseAgent
from models.base_model import BaseModel
from tools.file_tools import write_file
from utils.utils import extract_json

class SWArchitect(BaseAgent):
    input_schema = {
        "type": "object",
        "properties": {
            "prompt": {"type": "string"}
        },
        "required": ["prompt"]
    }

    output_schema = {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "type": "object",
          "required": ["project_name", "description", "file_structure", "component_schema"],
          "properties": {
            "project_name": {
              "type": "string",
              "description": "Name of the project"
            },
            "description": {
              "type": "string",
              "description": "Brief description of the project"
            },
            "file_structure": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["path", "description"],
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Path to the file relative to the project root"
                  },
                  "description": {
                    "type": "string",
                    "description": "Purpose and contents of this file"
                  }
                }
              }
            },
            "component_schema": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["name", "type", "description"],
                "properties": {
                  "name": {
                    "type": "string",
                    "description": "Name of the component"
                  },
                  "type": {
                    "type": "string",
                    "enum": ["abstract class", "class", "module", "function"],
                    "description": "Type of the component"
                  },
                  "description": {
                    "type": "string",
                    "description": "Purpose and functionality of this component"
                  },
                  "dependencies": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    },
                    "description": "List of other components this component depends on"
                  },
                  "methods": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "required": ["name", "description"],
                      "properties": {
                        "name": {
                          "type": "string",
                          "description": "Name of the method"
                        },
                        "description": {
                          "type": "string",
                          "description": "Purpose of this method"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }

    def __init__(self, llm: BaseModel):
        super().__init__(name="Software Architect", llm=llm)

    def run_agent(self, agent_input: dict) -> dict:
        if not self.validate_input(agent_input=agent_input, schema=self.input_schema):
            return {"error": "Invalid input data."}

        response = self._llm.send_message(agent_input["prompt"])
        data = extract_json(response.strip())
        write_file("architecture.txt", json.dumps(data))
        agent_output = data
        if not self.validate_output(agent_output=agent_output, schema=self.output_schema):
            return {"error": "Invalid output data."}

        return {"response": data}

