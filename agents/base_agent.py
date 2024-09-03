from abc import abstractmethod

from agents.agent_task import AgentTask, TaskType, OutputTarget

from models.base_model import BaseModel


class BaseAgent:
    def __init__(self, name):
        self._name: str = name
        self._response_handler = None
        self._llm: BaseModel | None = None
        self._task_list: list[AgentTask] = []
        self._active_task_idx: int = 0

    @property
    def task_list(self) -> list[AgentTask]:
        return self._task_list

    @task_list.setter
    def task_list(self, tasks: list[AgentTask]) -> None:
        self._task_list = tasks

    @property
    def active_task_id(self) -> int:
        return self._active_task_idx

    def run_task(self, task: AgentTask, task_input: str) -> str:
        """
        Runs the task with the specified input data
        :param task: the task to run
        :param task_input: any input data the task needs
        :return: the output of the task
        """
        output_data = ""
        if task.task_type == TaskType.LLM:
            output_data = self.process_llm_task(task_input, task.id)
        elif task.task_type == TaskType.FUNCTION:
            output_data = self.process_function_task(task_input, task.id)

        return output_data

    @abstractmethod
    def process_llm_task(self, instruction: str, id: str) -> str:
        pass

    @abstractmethod
    def process_function_task(self, instruction: str, id: str) -> str:
        pass
