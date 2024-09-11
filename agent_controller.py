from agents.task_flow import TaskFlow


class AgentController:
    """
    Manages the execution of a TaskFlow.

    This class holds a reference to a TaskFlow object and provides a method
    to run the flow. It ensures that the flow is properly initialized before
    execution.
    """
    def __init__(self):
        self._task_flow: TaskFlow | None = None

    @property
    def task_flow(self) -> TaskFlow:
        return self._task_flow

    @task_flow.setter
    def task_flow(self, flow: TaskFlow) -> None:
        self._task_flow = flow

    def run_task_flow(self) -> str:
        """
        Runs the associated TaskFlow and returns its result.

        Returns:
            str: The result of the TaskFlow execution. If no TaskFlow is
            associated, returns an empty string.
        """
        if self._task_flow is None:
            return ""
        return self.task_flow.run()
