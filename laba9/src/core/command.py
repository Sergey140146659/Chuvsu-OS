from enum import Enum, auto

class CommandType(Enum):
    COMPUTE = auto()
    IO = auto()
    EXIT = auto()


class Command:
    def __init__(self, type: CommandType):
        self.type = type

    def __repr__(self) -> str:
        return f"Command(type={self.type.name})"
