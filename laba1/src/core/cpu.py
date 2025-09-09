from .process import Process, ProcessState

class CPU:
    def execute(self, process: Process) -> None:
        if process is None:
            return

        process.state = ProcessState.RUNNING
        process.program_counter += 1
