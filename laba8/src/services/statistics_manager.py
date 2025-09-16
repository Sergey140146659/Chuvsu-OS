
from ..core.process import Process

class StatisticsManager:
    def __init__(self):
        self._completed_processes_count: int = 0
        self._total_wait_time: int = 0
        self._total_turnaround_time: int = 0
        self._total_mono_time: int = 0
        self.last_completed_process_report: dict = {}

    def register_process_completion(self, process: Process, completion_tick: int):
        self._completed_processes_count += 1
        turnaround_time = completion_tick - process.creation_tick

        self._total_wait_time += process.wait_time
        self._total_turnaround_time += turnaround_time
        self._total_mono_time += process.mono_execution_time

        self.last_completed_process_report = {
            "pid": process.pid,
            "t_mono": process.mono_execution_time,
            "t_multi": turnaround_time,
            "wait_time": process.wait_time,
            "overhead": turnaround_time - process.mono_execution_time
        }



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

    def get_average_mono_time(self) -> float:
        if self._completed_processes_count == 0:
            return 0.0
        return self._total_mono_time / self._completed_processes_count

    def get_performance_ratio(self) -> float:
        avg_mono = self.get_average_mono_time()
        avg_multi = self.get_average_turnaround_time()

        if avg_multi == 0:
            return 0.0

        return (avg_mono / avg_multi) * 100

    def get_last_process_report(self) -> dict:
        return self.last_completed_process_report
