# laba1/src/core/process.py

from enum import Enum
from itertools import count

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"

class Process:
    """Класс, представляющий процесс в системе."""
    
    _id_counter = count(0)

    def __init__(self, size: int):
        self.pid: int = next(self._id_counter)
        self.size: int = size
        self.program_counter: int = 0
        self.state: ProcessState = ProcessState.NEW

    def __repr__(self) -> str:
        return f"Process(pid={self.pid}, state={self.state.value}, pc={self.program_counter}, size={self.size})"

