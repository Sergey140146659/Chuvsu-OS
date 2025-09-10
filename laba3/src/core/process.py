from enum import Enum
from itertools import count

class ProcessState(Enum):
    NEW = "NEW"
    LOADING = "Загружается"
    READY = "Готов"
    RUNNING = "Выполняется"

    IO_INIT = "Иниц. I/O"
    IO_WAIT = "Ожид. I/O"

    BLOCKED_MEM = "Блок. память"
    SUSPENDED = "Приостановлен"

    TERMINATED = "Завершен"

class Process:
    _id_counter = count(0)

    def __init__(self, size: int):
        self.pid: int = next(self._id_counter)
        self.size: int = size
        self.program_counter: int = 0
        self.state: ProcessState = ProcessState.NEW
        self.ticks_worked_in_quantum: int = 0

    def __repr__(self) -> str:
        return f"Process(pid={self.pid}, state={self.state.value}, pc={self.program_counter}, size={self.size})"
