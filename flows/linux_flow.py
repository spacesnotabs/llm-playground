import subprocess
import json
import os
from datetime import datetime
from typing import List, Dict
from agents.linux_op_agent import LinuxOpAgent
from agents.console_agent import ConsoleAgent
from models.base_model import BaseModel


class LinuxFlow:
    def __init__(self, llm: BaseModel):
        """
        Initialize the Linux command execution flow.

        Args:
            llm (BaseModel): Language model instance to be used by the agents
        """
        self.linux_agent = LinuxOpAgent(llm)
        self.console_agent = ConsoleAgent(llm)
        self.history_dir = "history"
        os.makedirs(self.history_dir, exist_ok=True)
        
    def _execute_command(self, command: str) -> tuple[str, str, int]:
        """
        Execute a single Linux command and return its output.

        Args:
            command (str): The command to execute

        Returns:
            tuple: (stdout, stderr, return_code)
        """
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return stdout, stderr, process.returncode
        except Exception as e:
            return "", str(e), 1

    def _process_command_result(self, stdout: str, stderr: str, return_code: int) -> Dict:
        """
        Process command execution results using ConsoleAgent.

        Args:
            stdout (str): Standard output from command
            stderr (str): Standard error from command
            return_code (int): Command return code

        Returns:
            Dict: Console agent analysis results
        """
        console_output = stderr if stderr else stdout
        if not console_output and return_code == 0:
            console_output = "Command completed successfully with no output."
            
        return self.console_agent.run_agent({
            "console_output": console_output,
            "context": f"Return code: {return_code}"
        })

    def _generate_history_filename(self) -> str:
        """Generate a unique filename for the session history."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.history_dir, f"session_{timestamp}.json")

    def _save_session_history(self, history_data: Dict) -> None:
        """Save session history to a JSON file."""
        filename = self._generate_history_filename()
        with open(filename, 'w') as f:
            json.dump(history_data, f, indent=2)
        print(f"\nSession history saved to: {filename}")

    def run(self, task: str) -> None:
        """
        Run the Linux command flow.

        Args:
            task (str): The task description to be executed
        """
        print(f"\nStarting Linux task: {task}")
        error_feedback = None
        session_history = {
            "task": task,
            "commands": [],
            "timestamp": datetime.now().isoformat()
        }
        
        while True:
            # Get commands from LinuxOpAgent
            agent_response = self.linux_agent.run_agent({
                "task": task,
                "error_feedback": error_feedback
            })
            
            if "error" in agent_response:
                session_history["error"] = agent_response["error"]
                self._save_session_history(session_history)
                print(f"Error in Linux agent: {agent_response['error']}")
                break

            commands = agent_response["commands"]
            
            # Execute each command and process results
            for cmd_info in commands:
                command = cmd_info["command"]
                purpose = cmd_info["purpose"]
                
                print(f"\nExecuting: {command}")
                print(f"Purpose: {purpose}")
                
                stdout, stderr, return_code = self._execute_command(command)
                
                # Analyze command output
                analysis = self._process_command_result(stdout, stderr, return_code)
                
                # Record command execution in session history
                command_record = {
                    "command": command,
                    "purpose": purpose,
                    "status": analysis.get("status"),
                    "summary": analysis.get("summary"),
                    "return_code": return_code,
                    "timestamp": datetime.now().isoformat()
                }
                if "error" in analysis:
                    command_record["error"] = analysis["error"]
                session_history["commands"].append(command_record)
                
                if "error" in analysis:
                    print(f"Error analyzing output: {analysis['error']}")
                    continue
                
                print(f"Status: {analysis['status']}")
                print(f"Summary: {analysis['summary']}")
                print(f"Solution: {analysis['solution']['content']}")
                
                # If there's an error, get new commands with error feedback
                if analysis['status'] == 'error':
                    error_feedback = analysis['summary']
                    break
                
                error_feedback = None
            
            # If no error feedback, we're done
            if not error_feedback:
                session_history["status"] = "completed"
                self._save_session_history(session_history)
                print("\nTask completed successfully!")
                break
            
            print("\nRetrying with error feedback...")
