# laba1/src/services/scheduler.py

from typing import List, Optional
from collections import deque
from ..core.process import Process, ProcessState

class Scheduler:
    """Отвечает за выбор процесса для выполнения на CPU."""

    def __init__(self):
        self.ready_queue: deque[Process] = deque()

    def add_process(self, process: Process):
        """Добавляет процесс в очередь готовых к выполнению."""
        if process.state == ProcessState.NEW:
            process.state = ProcessState.READY
            self.ready_queue.append(process)

    def get_next_process(self) -> Optional[Process]:
        """
        Возвращает следующий процесс для выполнения.
        """
        if not self.ready_queue:
            return None
        
        return self.ready_queue[0]

    def remove_process(self, pid: int):
        """Удаляет процесс из очереди."""
        process_to_remove = None
        for p in self.ready_queue:
            if p.pid == pid:
                process_to_remove = p
                break
        
        if process_to_remove:
            self.ready_queue.remove(process_to_remove)

    @property
    def has_ready_processes(self) -> bool:
        """Проверяет, есть ли процессы в очереди."""
        return len(self.ready_queue) > 0
