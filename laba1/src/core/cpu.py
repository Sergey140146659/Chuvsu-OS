# laba1/src/core/cpu.py

from .process import Process, ProcessState

class CPU:
    """Эмулирует работу центрального процессора (CPU)."""

    def execute(self, process: Process) -> None:
        """
        Выполняет один такт для указанного процесса.
        Увеличивает счетчик команд и устанавливает статус RUNNING.
        """
        if process is None:
            return

        process.state = ProcessState.RUNNING
        process.program_counter += 1

