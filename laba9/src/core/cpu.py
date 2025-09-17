from typing import Optional

from .process import Process
from .command import Command, CommandType


class CPU:
    def __init__(self):
        self.current_process: Optional[Process] = None
        self.last_executed_command: Optional[Command] = None

    def _do_operation(self, command: Command) -> CommandType:
        return command.type

    def execute(self, process: Process, command: Command) -> CommandType:
        self.current_process = process
        self.last_executed_command = command
        process.program_counter += 1
        result_signal = self._do_operation(command)

        return result_signal
