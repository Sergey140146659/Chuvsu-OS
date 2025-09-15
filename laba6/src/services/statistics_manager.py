
from ..core.process import Process

class StatisticsManager:
    def __init__(self):
        self._completed_processes_count: int = 0
        self._total_wait_time: int = 0
        self._total_turnaround_time: int = 0

    def register_process_completion(self, process: Process, completion_tick: int):
        self._completed_processes_count += 1
        self._total_wait_time += process.wait_time

        turnaround_time = completion_tick - process.creation_tick
        self._total_turnaround_time += turnaround_time

    def get_average_wait_time(self) -> float:
        if self._completed_processes_count == 0:
            return 0.0
        return self._total_wait_time / self._completed_processes_count

    def get_average_turnaround_time(self) -> float:
        if self._completed_processes_count == 0:
            return 0.0
        return self._total_turnaround_time / self._completed_processes_count

    def get_completed_processes_count(self) -> int:
        return self._completed_processes_count
