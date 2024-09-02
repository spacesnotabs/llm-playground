from agents.task_flow import TaskFlow


class AgentController:
    def __init__(self):
        self._task_flow: TaskFlow | None = None

    @property
    def task_flow(self) -> TaskFlow:
        return self._task_flow

    @task_flow.setter
    def task_flow(self, flow: TaskFlow) -> None:
        self._task_flow = flow

    def run_task_flow(self) -> str:
        result = ""
        if self.task_flow:
            result = self.task_flow.run()

        return result
