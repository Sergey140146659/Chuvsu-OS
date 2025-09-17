from typing import List, Dict, Callable

from .scheduler import Scheduler
from .statistics_manager import StatisticsManager
from ..core.process import Process, ProcessState
from ..core.memory import MemoryManager
from ..services.process_manager import ProcessManager


class Regulator:
    def __init__(self,
                 process_table: Dict[int, Process],
                 ready_queue: Scheduler,
                 blocked_queue: List[Process],
                 memory_manager: MemoryManager,
                 process_manager: ProcessManager,
                 stats_manager: StatisticsManager,
                 get_system_tick: Callable[[], int]):

        self._process_table = process_table
        self._ready_queue = ready_queue
        self._blocked_queue = blocked_queue
        self._memory_manager = memory_manager
        self._process_manager = process_manager
        self._stats_manager = stats_manager
        self._get_system_tick = get_system_tick

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

    def handle_io_request(self, process_id: int, io_duration: int):
        process = self._process_table.get(process_id)
        if not process:
            return

        process.state = ProcessState.IO_WAIT
        process.io_time_remaining = io_duration
        self._blocked_queue.append(process)

    def handle_exit_interrupt(self, process_id: int):
        process = self._process_table.get(process_id)
        if not process:
            return

        self._stats_manager.register_process_completion(
            process=process,
            completion_tick=self._get_system_tick()
        )

        self._memory_manager.free(process_id)
        self._process_manager.remove_process(process_id)

        self._ready_queue.remove_process(process_id)
        if process in self._blocked_queue:
            self._blocked_queue.remove(process)

    def suspend_process(self, process_id: int) -> bool:
        process = self._process_table.get(process_id)
        if not process or process.state == ProcessState.SUSPENDED:
            return False

        if process.state == ProcessState.READY:
            self._ready_queue.remove_process(process_id)

        elif process.state == ProcessState.IO_WAIT:
            if process in self._blocked_queue:
                self._blocked_queue.remove(process)

        process.state = ProcessState.SUSPENDED
        return True

    def resume_process(self, process_id: int) -> bool:
        process = self._process_table.get(process_id)
        if not process or process.state != ProcessState.SUSPENDED:
            return False

        process.state = ProcessState.READY
        self._ready_queue.add_process(process)
        return True

    def kill_process(self, process_id: int) -> bool:
        process = self._process_table.get(process_id)
        if not process:
            return False

        if process in self._ready_queue.ready_queue:
             self._ready_queue.remove_process(process_id)

        if process in self._blocked_queue:
            self._blocked_queue.remove(process)

        self._memory_manager.free(process_id)
        self._process_manager.remove_process(process_id)

        return True
