from time import sleep

from agents.agent_task import AgentTask, ExecType
from agents.base_agent import BaseAgent


class TaskFlow:
    def __init__(self):
        self._tasks: list[AgentTask] = []
        self._agents: list[BaseAgent] = []
        self._debug = True

    def run_task(self, agent: BaseAgent, task: AgentTask, task_input: str) -> str:
        """
        Calls an agent's run_task method

        :param agent: the agent to use
        :param task: the task to run
        :param task_input: input to the task
        :return: output of the task
        """
        if self._debug:
            print("\nTaskFlow:run_task")
            print('*'*20)
            print(agent)
            print(task)
            print('task_input:', task_input)
            print('*'*20)
            print('\n')

        return agent.run_task(task=task, task_input=task.instruction + task_input)

    def run_task_loop(self, agent: BaseAgent, task: AgentTask, task_input: str) -> str:
        timeout = 5 # safety mechanism, timeout after 5 loops
        while timeout > 0:
            timeout -= 1
            for subtask in task.subtasks:
                task_input = self.run_task(agent=agent, task=subtask, task_input=task_input)
                sleep(5)
            if task.loop_exit in task_input:
                print("Loop exit found!")
                break

        return task_input

    def run_task_cond(self, agent: BaseAgent, task: AgentTask,  task_input: str) -> str:
        if input == task.conditional:
            output = self.run_task(agent=agent, task=task.subtasks[0], task_input=task_input)
        else:
            output = self.run_task(agent=agent, task=task.subtasks[1], task_input=task_input)
        return output

    def run(self) -> str:
        if self._debug:
            print('TaskFlow:run()')
            print('*'*30)

        agent = self._agents[0]
        if self._debug:
            print('Using agent ', agent)

        task_output = ""
        for task in self._tasks:
            if task.exec_type == ExecType.SINGLE:
                task_output = self.run_task(agent=agent, task=task, task_input=task_output)
            elif task.exec_type == ExecType.LOOP:
                task_output = self.run_task_loop(agent=agent, task=task, task_input=task_output)
            elif task.exec_type == ExecType.CONDITIONAL:
                task_output = self.run_task_cond(agent=agent, task=task, task_input=task_output)

        if self._debug:
            print('returning output ', task_output)
            print('*' * 30)

        return task_output

    def add_task(self, task: AgentTask) -> None:
        self._tasks.append(task)

    def add_agent(self, agent: BaseAgent) -> None:
        self._agents.append(agent)
