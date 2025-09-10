from typing import List, Optional
from collections import deque
from ..core.process import Process, ProcessState

class Scheduler:
    def __init__(self):
        self.ready_queue: deque[Process] = deque()

    def add_process(self, process: Process):
        if process.state in [ProcessState.NEW, ProcessState.RUNNING, ProcessState.READY]:
            process.state = ProcessState.READY
            self.ready_queue.append(process)

    def get_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None

        return self.ready_queue.popleft()

    def remove_process(self, pid: int):
        process_to_remove = None
        for p in self.ready_queue:
            if p.pid == pid:
                process_to_remove = p
                break

        if process_to_remove:
            self.ready_queue.remove(process_to_remove)

    @property
    def has_ready_processes(self) -> bool:
        return len(self.ready_queue) > 0
