from enum import Enum, auto

class CommandType(Enum):
    COMPUTE = auto()  # Вычислительная операция
    IO = auto()       # Операция ввода-вывода
    EXIT = auto()     # Команда завершения процесса


class Command:
    def __init__(self, type: CommandType):
        self.type = type

    def __repr__(self) -> str:
        return f"Command(type={self.type.name})"
