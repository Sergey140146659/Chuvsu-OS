from typing import Optional
from .process import Process, ProcessState

class CPU:
    def __init__(self):
        self.current_process: Optional[Process] = None

    def execute(self, process: Process) -> None:
        if process is None:
            self.current_process = None
            return

        self.current_process = process
        self.current_process.state = ProcessState.RUNNING
        self.current_process.program_counter += 1
