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
        self._current_loop_state: dict | None = None

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
        print(f"Starting workflow: {self._workflow['name']}")

    def execute_workflow(self):
        if self._current_loop_state:
            self.handle_loop(self._current_loop_state['step'])
        elif self._current_step:
            self.execute_step(self._current_step)

        return not self._waiting_for_input and self._current_step is not None

    def execute_step(self, step: dict):
        """Executes the workflow from the current step."""
        step_type = step['type']
        step_id = self._current_step['id']

        print(f"Executing step {step_id}: {self._current_step['description']}")

        if step_type == 'user_input':
            self.handle_user_input(self._current_step)
            return # wait for user input
        elif step_type == 'agent_action':
            self.handle_agent_action(self._current_step)
        elif step_type == 'system_action':
            self.handle_system_action(self._current_step)
        elif step_type == 'loop':
            self.handle_loop(self._current_step)
        else:
            print(f"Unknown step type: {step_type}")

        self.transition_to_next_step()

    def handle_user_input(self, step, user_input: dict | None = None):
        print('Handling user input')
        input_prompt: str = ''

        # combine output from previous step to include in prompt
        if self._state:
            for item in step['prepend']:
                input_prompt += f'\n{self._state[item]}\n'

        # prepare prompt to send to user
        for item in step['input'].values():
            input_prompt += f'\n{item}\n'

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

            self._state["code_to_modify"] = ''
            file_content = read_file(self._state["filepath"])
            self._state["code_to_modify"] += file_content

            self._state["context"] = ""
            for file in self._state["context_files"]:
                self._state["context"] += f"{file}\n\n{read_file(file)}\n"

        elif tool_to_use == "file_write":
            result = write_file(self._state["files_to_modify"], self._state["modified_code"])
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

    def handle_loop(self, step):
        """Executes a loop step (repeat action for multiple items or indefinitely)."""
        loop_over_list = step['loop_over'].split('.')[0]
        loop_over_item = step['loop_over'].split('.')[1]

        if not self._current_loop_state:
            # first time entering this function so create a new loop state
            self._current_loop_state = {
                'parent_step': step,
                'items': self._state.get(loop_over_list, []),
                'current_index': 0,
                'current_sub_step': 0
            }

        if self._current_loop_state['current_index'] < len(self._current_loop_state['items']):
            # more sub_steps to run
            item = self._current_loop_state['items'][self._current_loop_state['current_index']]
            self._state[loop_over_item] = item
            self._current_step = step['sub-steps'][self._current_loop_state['current_sub_step']]
            self.execute_step(self._current_step)
        else:
            self._current_loop_state = None
            self.resume_workflow()

        # loop_over = step.get('loop_over', None)
        # print(f"Handling loop over parameter {loop_over}")
        # if loop_over:
        #     str_parts = loop_over.split('.')
        #     loop_list = self._state.get(str_parts[0])
        #     input_name = str_parts[1]  # get the second part of the string to use as state data for the loop
        #
        #     print(f"  Iterating over {loop_list} for each {input_name}")
        #     for item in loop_list:
        #         self._state[input_name] = item
        #         print(f"    Processing {item}")
        #         for loop_step in step['steps']:
        #             self._current_step = loop_step
        #             self.execute_workflow()
        #
        # self._current_step = step
        # print('Loop complete')

    def resume_workflow(self):
        if self._current_loop_state:
            self._current_loop_state['current_index'] += 1
            self.handle_loop(self._current_loop_state['parent_step'])
        else:
            self.transition_to_next_step()
        self.execute_workflow()

    def transition_to_next_step(self):
        """Handle transition logic to the next step."""
        # print('Transitioning to next step with current state: ', self._state)
        next_step = self._current_step.get('next_step', 0)
        print('Transitioning to step: ', next_step)
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
