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
    output_target: OutputTarget
    instruction: str = field(default_factory=str)
    loop_exit: str = field(default_factory=str)
    conditional: str = field(default_factory=str)
    subtasks: List['AgentTask'] = field(default_factory=list)
