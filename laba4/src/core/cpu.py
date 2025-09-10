
import random
from typing import Optional

from .process import Process
from .command import Command, CommandType


class CPU:
    def __init__(self, io_command_probability: float):
        self.current_process: Optional[Process] = None
        self.io_command_probability = io_command_probability
        self.last_executed_command: Optional[Command] = None

    def _fetch_command(self, process: Process) -> Command:
        if process.program_counter >= process.program_length:
            return Command(type=CommandType.EXIT)

        if random.random() < self.io_command_probability:
            return Command(type=CommandType.IO)

        return Command(type=CommandType.COMPUTE)

    def _do_operation(self, command: Command) -> CommandType:
        return command.type

    def execute(self, process: Process) -> CommandType:
        self.current_process = process
        command = self._fetch_command(process)
        self.last_executed_command = command
        process.program_counter += 1
        result_signal = self._do_operation(command)
        return result_signal
