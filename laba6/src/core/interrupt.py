from enum import Enum, auto

class InterruptType(Enum):
    TIMER = auto()      # Сигнал от таймера (квант времени истек)
    IO_DONE = auto()    # Сигнал о завершении операции ввода-вывода
    PROCESS_EXIT = auto() # Сигнал о том, что процесс выполнил команду выхода


class Interrupt:
    def __init__(self, type: InterruptType, process_id: int):
        self.type = type
        self.process_id = process_id

    def __repr__(self) -> str:
        return f"Interrupt(type={self.type.name}, pid={self.process_id})"
