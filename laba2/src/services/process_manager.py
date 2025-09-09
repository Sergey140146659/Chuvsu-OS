from typing import Dict, Optional, List
from ..core.process import Process

class ProcessManager:
    def __init__(self, max_processes: int):
        self.max_processes: int = max_processes
        self.process_table: Dict[int, Process] = {}

    def is_table_full(self) -> bool:
        return len(self.process_table) >= self.max_processes

    def create_and_register_process(self, size: int) -> Optional[Process]:
        if self.is_table_full():
            return None

        new_process = Process(size=size)
        self.process_table[new_process.pid] = new_process
        return new_process

    def register_process(self, process: Process) -> bool:
        if self.is_table_full():
            return False

        self.process_table[process.pid] = process
        return True

    def get_process(self, pid: int) -> Optional[Process]:
        return self.process_table.get(pid)

    def remove_process(self, pid: int) -> bool:
        if pid in self.process_table:
            del self.process_table[pid]
            return True
        return False

    def get_all_pids(self) -> List[int]:
        return list(self.process_table.keys())

    def __repr__(self) -> str:
        return f"ProcessManager(count={len(self.process_table)}/{self.max_processes})"
