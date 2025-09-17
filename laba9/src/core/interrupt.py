from enum import Enum, auto

class InterruptType(Enum):
    TIMER = auto()
    IO_DONE = auto()
    PROCESS_EXIT = auto()


class Interrupt:
    def __init__(self, type: InterruptType, process_id: int):
        self.type = type
        self.process_id = process_id

    def __repr__(self) -> str:
        return f"Interrupt(type={self.type.name}, pid={self.process_id})"
