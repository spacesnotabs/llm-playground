import json

from agents.base_agent import BaseAgent
from tools.file_tools import read_file, write_file


class WorkflowController:
    def __init__(self, input_provider):
        self._workflow: dict | None = None
        self._current_step: dict | None = None
        self._input_provider = input_provider
        self._agent: BaseAgent | None = None
        self._state = {}  # Store inputs/outputs for passing between steps
        self._waiting_for_input = False
        self._is_running = False
        self._message_handler = None

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        self._is_running = value

    @property
    def message_handler(self):
        return self._message_handler

    @message_handler.setter
    def message_handler(self, handler):
        if handler:
            self._message_handler = handler

    def set_agent(self, agent: BaseAgent) -> None:
        self._agent = agent

    def load_workflow(self, workflow_id: str):
        """Load the workflow and initialize the first step."""
        try:
            with open(f'workflows/{workflow_id}.json', 'r') as f:
                self._workflow = json.load(f)
        except FileNotFoundError:
            print(f"No workflow with name {workflow_id} found.")
            return

        self._current_step = self._workflow['steps'][0]  # Start at the first step

    def execute_workflow(self):
        print('execute_workflow()')
        while True:
            while self._current_step:
                self.execute_step(self._current_step)

                if self._waiting_for_input:
                    return  # exit workflow as we wait for response

                self.transition_to_next_step()

            # if we get here, the workflow has finished
            print('Workflow complete. Starting over.')
            self._current_step = self._workflow['steps'][0]  # Start at the first step
            self.start_workflow()

    def execute_step(self, step: dict):
        """Executes the workflow from the current step."""
        step_type = step['type']
        step_id = self._current_step['id']

        print(f"Executing step {step_id}: {self._current_step}")

        if step_type == 'user_input':
            self.handle_user_input(self._current_step)
            return # wait for user input
        elif step_type == 'agent_action':
            self.handle_agent_action(self._current_step)
            print('agent_action step handled')
        elif step_type == 'system_action':
            self.handle_system_action(self._current_step)
            print('system_action step handled')
        else:
            print(f"Unknown step type: {step_type}")

    def handle_user_input(self, step, user_input: dict | None = None):
        print('Handling user input')
        input_prompt: str = ''

        # combine output from previous step to include in prompt
        if self._state:
            for item in step.get('prepend', []):
                input_prompt += f'{self._state[item]}\n\n'

        # prepare prompt to send to user
        for item in step['input'].values():
            input_prompt += f'{item}\n\n'

        self._waiting_for_input = True
        self._input_provider(input_prompt)

    def handle_system_action(self, step):
        """Simulates user input (for demo purposes)."""
        input_prompt = step['description']
        tool_to_use = step['agent']

        print(f"Performing system action {input_prompt} using tool {tool_to_use} ")

        # get appropriate tool (function)

        # Collect the necessary inputs from the state
        input_keys = step['input']
        inputs = {key: self._state.get(key, None) for key in input_keys}
        # print("inputs to handle_system_action are ", inputs)

        # the inputs must match the number and order of the outputs from the workflow json

        # run the system tool on the inputs
        output_data = []

        if tool_to_use == "file_read":

            self._input_provider('Reading file')
            self._state["code_to_modify"] = ''
            file_content = read_file(self._state["files_to_modify"][0])
            self._state["code_to_modify"] += file_content

            self._state["context"] = ""
            for file in self._state["context_files"]:
                self._state["context"] += f"{file} {read_file(file)} "

        elif tool_to_use == "file_write":
            self._input_provider('Writing file')
            result = write_file(self._state["files_to_modify"][0], self._state["modified_code"])
            self._state["result_of_write"] = result

        # print("handle_system_action outputting ", self._state)

    def handle_agent_action(self, step):
        """Simulates an agent performing an action (replace with actual agent logic)."""
        agent = step['agent']
        action = step['description']

        print(f"Performing agent action with agent {agent} and action {action}")

        # Collect the necessary inputs from the state
        input_keys = step['input']
        inputs = {key: self._state.get(key, None) for key in input_keys}

        agent_output = self._agent.run_agent(inputs)

        # the output of the agent should have the same keys as step['output']
        for output in step['output']:
            self._state[output] = agent_output[output]

    def transition_to_next_step(self):
        """Handle transition logic to the next step."""
        # print('Transitioning to next step with current state: ', self._state)
        next_step = self._current_step.get('next_step', 0)
        # print('Transitioning to step: ', next_step)
        if not next_step:
            print('exit workflow')
            self._current_step = None
            return

        if isinstance(next_step, dict):
            # Conditional next step (on success/failure)
            condition = self._state.get(self._current_step['output'][0], None)
            if condition.lower() == 'yes':
                next_step_id = next_step['on_success']
            else:
                next_step_id = next_step['on_failure']
        else:
            # Simple next step
            next_step_id = next_step

        self._current_step = self.get_step_by_id(next_step_id)

    def get_step_by_id(self, step_id):
        """Find a step by its ID."""
        print('get_step_by_id: ', step_id)
        for step in self._workflow['steps']:
            if step['id'] == step_id:
                return step
        return None

    def set_user_input(self, user_input: dict):
        if self._waiting_for_input:
            print('set_user_input received: ', user_input)
            for output_key in self._current_step['output']:
                self._state[output_key] = user_input.get(output_key, None)

            self._waiting_for_input = False
            self.transition_to_next_step()
            self.execute_workflow()

    def exit_workflow(self):
        """Cleanup and stop running the workflow."""
        self._workflow = None
        self._current_step = None
        self._state = {}
        self._waiting_for_input = False
        self.is_running = False
        print("Workflow exited")

    def start_workflow(self):
        self._is_running = True
        self.execute_workflow()

    def _post_message(self, message: str) -> None:
        if self._message_handler:
            self._message_handler(message)