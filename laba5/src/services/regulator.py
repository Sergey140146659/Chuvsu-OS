from typing import List, Dict

from .scheduler import Scheduler
from ..core.process import Process
from ..core.memory import MemoryManager
from ..services.process_manager import ProcessManager
from ..core.process import ProcessState


class Regulator:
    def __init__(self,
                 process_table: Dict[int, Process],
                 ready_queue: Scheduler,
                 blocked_queue: List[Process],
                 memory_manager: MemoryManager,
                 process_manager: ProcessManager):

        self._process_table = process_table
        self._ready_queue = ready_queue
        self._blocked_queue = blocked_queue
        self._memory_manager = memory_manager
        self._process_manager = process_manager

    def handle_timer_interrupt(self, process_id: int):
        process = self._process_table.get(process_id)
        if not process:
            return
        process.state = ProcessState.READY
        self._ready_queue.add_process(process)

    def handle_io_done_interrupt(self, process_id: int):
        process_to_unblock = None
        for p in self._blocked_queue:
            if p.pid == process_id:
                process_to_unblock = p
                break

        if not process_to_unblock:
            return

        self._blocked_queue.remove(process_to_unblock)
        process_to_unblock.state = ProcessState.READY
        self._ready_queue.add_process(process_to_unblock)

    def handle_exit_interrupt(self, process_id: int):
        if process_id not in self._process_table:
            return

        self._memory_manager.free(process_id)
        self._process_manager.remove_process(process_id)
        self._ready_queue.remove_process(process_id)
        process_to_remove = None
        for p in self._blocked_queue:
            if p.pid == process_id:
                process_to_remove = p
                break
        if process_to_remove:
            self._blocked_queue.remove(process_to_remove)

    def handle_io_request(self, process_id: int, io_duration: int):
        process = self._process_table.get(process_id)
        if not process:
            return

        process.state = ProcessState.IO_WAIT
        process.io_time_remaining = io_duration
        self._blocked_queue.append(process)
