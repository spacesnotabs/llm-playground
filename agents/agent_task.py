from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ExecType(Enum):
    SINGLE = 0
    LOOP = 1
    CONDITIONAL = 2


class TaskType(Enum):
    FUNCTION = 0
    LLM = 1


class OutputTarget(Enum):
    USER = 0
    NEXT_TASK = 1


@dataclass
class AgentTask:
    exec_type: ExecType
    task_type: TaskType
    id: str
    output_target: OutputTarget = OutputTarget.NEXT_TASK  # Default output target
    input_data: dict = field(default_factory=dict)
    loop_exit: str = field(default_factory=str)
    conditional: str = field(default_factory=str)
    subtasks: List['AgentTask'] = field(default_factory=list)

    def __post_init__(self):
        if self.exec_type == ExecType.LOOP and not isinstance(self.loop_exit, str):
            raise ValueError("loop_exit must be a string for loop tasks")
        if self.exec_type == ExecType.CONDITIONAL and not isinstance(self.conditional, str):
            raise ValueError("conditional must be a string for conditional tasks")


def _create_task(input_data: dict, task_id: str, task_type: TaskType, exec_type: ExecType = ExecType.SINGLE,
                 loop_exit: str = "") -> AgentTask:
    """
    Helper function to create a task with common attributes.

    Args:
        task_id: The unique identifier for the task.
        task_type: The type of the task (function or LLM).
        exec_type: The execution type of the task (single, loop, or conditional).
        loop_exit: The condition for exiting a loop (only relevant for loop tasks).

    Returns:
        An AgentTask object representing the created task.
    """
    return AgentTask(
        input_data=input_data,
        id=task_id,
        task_type=task_type,
        exec_type=exec_type,
        loop_exit=loop_exit,
        conditional="",
        output_target=OutputTarget.NEXT_TASK
    )


def create_llm_task(input_data: dict, task_id: str, exec_type: ExecType = ExecType.SINGLE, loop_exit: str = "") -> AgentTask:
    """
    Creates a new LLM task.

    Args:
        task_id: The unique identifier for the task.
        exec_type: The execution type of the task (single, loop, or conditional).
        loop_exit: The condition for exiting a loop (only relevant for loop tasks).

    Returns:
        An AgentTask object representing the created LLM task.
    """
    return _create_task(input_data=input_data, task_id=task_id, task_type=TaskType.LLM,
                        exec_type=exec_type, loop_exit=loop_exit)


def create_func_task(input_data: dict, task_id: str, exec_type: ExecType = ExecType.SINGLE,
                     loop_exit: str = "") -> AgentTask:
    """
    Creates a new function task.

    Args:
        task_id: The unique identifier for the task.
        exec_type: The execution type of the task (single, loop, or conditional).
        loop_exit: The condition for exiting a loop (only relevant for loop tasks).

    Returns:
        An AgentTask object representing the created function task.
    """
    return _create_task(input_data=input_data, task_id=task_id, task_type=TaskType.FUNCTION,
                        exec_type=exec_type, loop_exit=loop_exit)


def create_loop_task(input_data: dict, subtasks: List[AgentTask], task_id: str, loop_exit: str) -> AgentTask:
    """
    Creates a new loop task.

    Args:
        subtasks: A list of subtasks to be executed within the loop.
        task_id: The unique identifier for the task.
        loop_exit: The condition for exiting the loop.

    Returns:
        An AgentTask object representing the created loop task.
    """
    if not isinstance(loop_exit, str):
        raise ValueError("loop_exit must be a string")
    return AgentTask(
        input_data=input_data,
        id=task_id,
        task_type=TaskType.LLM,
        exec_type=ExecType.LOOP,
        loop_exit=loop_exit,
        conditional="",
        output_target=OutputTarget.NEXT_TASK,
        subtasks=subtasks
    )


def create_conditional_task(input_data: dict, subtasks: List[AgentTask], task_id: str, conditional: str) -> AgentTask:
    """
    Creates a new conditional task.

    Args:
        subtasks: A list of subtasks to be executed based on the condition.
        task_id: The unique identifier for the task.
        conditional: The condition that determines whether the subtasks are executed.

    Returns:
        An AgentTask object representing the created conditional task.
    """
    if not isinstance(conditional, str):
        raise ValueError("conditional must be a string")
    return AgentTask(
        input_data=input_data,
        id=task_id,
        task_type=TaskType.LLM,
        exec_type=ExecType.CONDITIONAL,
        loop_exit="",
        conditional=conditional,
        output_target=OutputTarget.NEXT_TASK,
        subtasks=subtasks
    )
