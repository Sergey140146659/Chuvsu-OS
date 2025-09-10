import time
from typing import Dict, Optional

from .core.cpu import CPU
from .core.memory import MemoryManager
from .core.process import Process
from .services.process_manager import ProcessManager
from .services.scheduler import Scheduler
from .core.process import ProcessState
from .core.command import Command, CommandType

class OperatingSystem:
    def __init__(self, config: Dict):
        self.cpu = CPU(io_command_probability=config['io_command_probability'])
        self.memory_manager = MemoryManager(total_size=config['memory'])
        self.process_manager = ProcessManager(max_processes=config['max_processes'])
        self.scheduler = Scheduler()
        self.default_process_size: int = config.get('default_process_size', 128)
        self.next_task_to_load: Optional[Process] = None
        self.speed_hz: float = config.get('initial_speed_hz', 1.0)
        self._running: bool = False
        self.quantum_length: int = config.get('quantum_length', 5)
        self.active_process: Optional[Process] = None

        self.program_length: int = config.get('program_length', 30)
        self.io_command_probability: float = config.get('io_command_probability', 0.2)
        self.io_duration: int = config.get('io_duration', 15)
        self.cpu = CPU(io_command_probability=self.io_command_probability)
        self.blocked_queue: list[Process] = []

    def _generate_new_task(self) -> None:
        if self.process_manager.is_table_full():
            self.next_task_to_load = None
            return

        new_task = Process(size=self.default_process_size, program_length=self.program_length)
        self.next_task_to_load = new_task

    def _load_next_task(self) -> bool:
        task_to_load = self.next_task_to_load

        if not task_to_load:
            return False

        if self.process_manager.is_table_full():
            return False

        if not self.memory_manager.has_enough_space(task_to_load.size):
            return False

        self.process_manager.register_process(task_to_load)

        self.memory_manager.allocate(task_to_load.pid, task_to_load.size)

        self.scheduler.add_process(task_to_load)

        self.next_task_to_load = None

        return True

    def boot(self):
        print("Загрузка ОС...")

        self._generate_new_task()

        print("Начальная загрузка процессов в память...")
        while self._load_next_task():
            self._generate_new_task()

        print("Начальная загрузка завершена. Запуск основного цикла симуляции.")

        self._running = True
        self.run()

    def shutdown(self):
        self._running = False

    def run(self):
        while self._running:
            self._handle_blocked_processes()

            if self.active_process is None:
                if self.scheduler.has_ready_processes:
                    self.active_process = self.scheduler.get_next_process()
                    if self.active_process:
                        self.active_process.ticks_worked_in_quantum = 0
                        self.active_process.state = ProcessState.RUNNING
            if self.active_process is None and self.scheduler.has_ready_processes:
                self.active_process = self.scheduler.get_next_process()
                if self.active_process:
                    self.active_process.ticks_worked_in_quantum = 0

            if self.active_process:
                process = self.active_process
                process.state = ProcessState.RUNNING

                result_signal = self.cpu.execute(process)
                process.ticks_worked_in_quantum += 1

                if result_signal == CommandType.IO:
                    self._block_process_for_io(process)
                elif result_signal == CommandType.EXIT:
                    self._terminate_process(process)
                elif process.ticks_worked_in_quantum >= self.quantum_length:
                    self.scheduler.add_process(process)
                    self.active_process = None

            time.sleep(1.0 / self.speed_hz if self.speed_hz > 0 else 0.1)



    def create_new_process(self, size: int) -> str:
        if self.process_manager.is_table_full():
            return "Ошибка: Таблица процессов заполнена."

        if not self.memory_manager.has_enough_space(size):
            return f"Ошибка: Недостаточно памяти. Требуется {size}, доступно {self.memory_manager.total_size - self.memory_manager.used_memory}."

        new_process = self.process_manager.create_and_register_process(
            size=size, program_length=self.program_length
        )

        if new_process is None:
            return "Ошибка: Не удалось создать процесс."

        if not self.memory_manager.allocate(new_process.pid, new_process.size):
            self.process_manager.remove_process(new_process.pid)
            return "Ошибка: Не удалось выделить память."

        self.scheduler.add_process(new_process)

        return f"Процесс {new_process.pid} успешно создан."


    def get_system_stats(self) -> Dict:
        all_processes = list(self.process_manager.process_table.values())
        cpu_state = "Работа" if self.active_process else "Ожидание"

        last_command = self.cpu.last_executed_command if self.cpu.last_executed_command else "N/A"

        stats = {
            "speed_hz": round(self.speed_hz, 2),
            "memory_usage": f"{self.memory_manager.used_memory}/{self.memory_manager.total_size}",
            "process_count": f"{len(self.process_manager.process_table)}/{self.process_manager.max_processes}",
            "all_processes": all_processes,
            "next_task": self.next_task_to_load,
            "active_pid": self.active_process.pid if self.active_process else "N/A",
            "cpu_state": cpu_state,
            "blocked_count": len(self.blocked_queue),
            "last_command": str(last_command)
        }
        return stats

    def change_speed(self, factor: float):
        new_speed = self.speed_hz * factor
        self.speed_hz = max(0.1, min(1000.0, new_speed))

    def _handle_blocked_processes(self) -> None:
        processes_to_unblock = []
        for process in self.blocked_queue:
            process.io_time_remaining -= 1
            if process.io_time_remaining <= 0:
                processes_to_unblock.append(process)

        for process in processes_to_unblock:
            self.blocked_queue.remove(process)
            process.state = ProcessState.READY
            self.scheduler.add_process(process)

    def _block_process_for_io(self, process: Process) -> None:
        process.state = ProcessState.IO_WAIT
        process.io_time_remaining = self.io_duration
        self.blocked_queue.append(process)
        self.active_process = None

    def _terminate_process(self, process: Process) -> None:
        pid = process.pid
        self.memory_manager.free(pid)
        self.scheduler.remove_process(pid)
        self.process_manager.remove_process(pid)
        if self.active_process and self.active_process.pid == pid:
            self.active_process = None
