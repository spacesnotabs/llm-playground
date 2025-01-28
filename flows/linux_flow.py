import subprocess
from typing import List, Dict
from agents.linux_op_agent import LinuxOpAgent
from agents.console_agent import ConsoleAgent
from models.base_model import BaseModel
from time import sleep
import logging
from datetime import datetime


class LinuxFlow:
    def __init__(self, llm_linux: BaseModel, llm_console: BaseModel):
        """
        Initialize the Linux command execution flow.

        Args:
            llm_linux (BaseModel): Language model instance for Linux commands
            llm_console (BaseModel): Language model instance for console analysis
        """
        self.linux_agent = LinuxOpAgent(llm_linux)
        self.console_agent = ConsoleAgent(llm_console)
        self.command_history: list[str] = []
        
        # Setup logging
        log_filename = f"logs/linux_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _execute_command(self, command: str) -> tuple[str, str, int]:
        """
        Execute a single Linux command and return its output.

        Args:
            command (str): The command to execute

        Returns:
            tuple: (stdout, stderr, return_code)
        """
        try:
            self.logger.info(f"Executing command: {command}")
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_data = []
            stderr_data = []
            
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    line = f"OUT: {stdout_line.strip()}"
                    print(line)
                    self.logger.info(line)
                    stdout_data.append(stdout_line)
                    
                if stderr_line:
                    line = f"ERR: {stderr_line.strip()}"
                    print(line)
                    self.logger.error(line)
                    stderr_data.append(stderr_line)
                    
                if process.poll() is not None:
                    break
            
            return_code = process.returncode
            self.logger.info(f"Command completed with return code: {return_code}")
            return ''.join(stdout_data), ''.join(stderr_data), return_code
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Exception during command execution: {error_msg}")
            return '', error_msg, 1

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
                
                self.command_history.append(command)

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
                sleep(2)
            
            # If no error feedback, we're done
            if not error_feedback:
                print("\nTask completed successfully!")
                break
            
            print("\nRetrying with error feedback...")

        # Output results
        print("Requested task: ", task)
        self.output_command_history() 
        self.command_history.clear()

    def output_command_history(self) -> None:
        """
        Output the command history to the console.
        """
        print("\nCommand History:")
        for i, command in enumerate(self.command_history, start=1):
            print(f"{i}. {command}")