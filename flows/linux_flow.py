import subprocess
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

    def run(self, task: str) -> None:
        """
        Run the Linux command flow.

        Args:
            task (str): The task description to be executed
        """
        print(f"\nStarting Linux task: {task}")
        error_feedback = None
        
        while True:
            # Get commands from LinuxOpAgent
            agent_response = self.linux_agent.run_agent({
                "task": task,
                "error_feedback": error_feedback
            })
            
            if "error" in agent_response:
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
                print("\nTask completed successfully!")
                break
            
            print("\nRetrying with error feedback...")
