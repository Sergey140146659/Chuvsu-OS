import random
import time
from typing import Dict, List, Optional
from .config_loader import ConfigLoader

from .core.cpu import CPU
from .core.memory import MemoryManager
from .core.process import Process, ProcessState
from .core.command import Command, CommandType
from .core.interrupt import Interrupt, InterruptType

from .services.process_manager import ProcessManager
from .services.scheduler import Scheduler
from .services.regulator import Regulator
from .services.statistics_manager import StatisticsManager
from collections import deque

class OperatingSystem:
    def __init__(self, system_config: Dict, config_loader: ConfigLoader):
        self.config_loader = config_loader

        self.memory_size = system_config.get('memory', 1024)
        self.max_processes = system_config.get('max_processes', 10)
        self.quantum_length = system_config.get('quantum_length', 5)
        self.io_duration = system_config.get('io_duration', 15)
        self.speed_hz: float = system_config.get('initial_speed_hz', 1.0)

        self.cpu = CPU()
        self.memory_manager = MemoryManager(total_size=self.memory_size)
        self.process_manager = ProcessManager(max_processes=self.max_processes)
        self.scheduler = Scheduler()
        self.blocked_queue: list[Process] = []
        self._interrupt_queue: list[Interrupt] = []
        self.stats_manager = StatisticsManager()

        self.regulator = Regulator(
            process_table=self.process_manager.process_table,
            ready_queue=self.scheduler,
            blocked_queue=self.blocked_queue,
            memory_manager=self.memory_manager,
            process_manager=self.process_manager,
            stats_manager=self.stats_manager,
            get_system_tick=lambda: self.system_tick
        )

        self.active_process: Optional[Process] = None
        self.next_task_to_load: Optional[Process] = None
        self._running: bool = False
        self.system_tick: int = 0
        self.execution_history: deque = deque(maxlen=16)

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
            self.system_tick += 1

            for p in list(self.scheduler.ready_queue):
                p.wait_time += 1

            if self.active_process:
                process = self.active_process
                process.mono_execution_time += 1
                process.ticks_worked_in_quantum += 1

                command = self._generate_command(process)
                signal = self.cpu.execute(process, command)

                if signal == CommandType.IO:
                    self.regulator.handle_io_request(process.pid, self.io_duration)
                    self.active_process = None
                elif signal == CommandType.EXIT:
                    self._interrupt_queue.append(Interrupt(InterruptType.PROCESS_EXIT, process.pid))

            for p in self.blocked_queue:
                p.io_time_remaining -= 1
                p.mono_execution_time += 1

            self._check_for_interrupts()
            self._handle_interrupts()

            if self.active_process is None:
                if self.scheduler.has_ready_processes:
                    self.active_process = self.scheduler.get_next_process()
                    if self.active_process:
                        self.active_process.ticks_worked_in_quantum = 0
                        self.execution_history.append(self.active_process.pid)
                else:
                    if self._load_next_task():
                        self._generate_new_task()

            time.sleep(1.0 / self.speed_hz if self.speed_hz > 0 else 0.1)


    def _generate_command(self, process: Process) -> Command:
        if process.program_counter >= process.program_length:
            return Command(type=CommandType.EXIT)

        if random.random() < process.io_probability:
            return Command(type=CommandType.IO)

        return Command(type=CommandType.COMPUTE)

    def _check_for_interrupts(self):
        for process in self.blocked_queue:
            if process.io_time_remaining <= 0:
                self._interrupt_queue.append(Interrupt(InterruptType.IO_DONE, process.pid))

        if self.active_process and self.active_process.ticks_worked_in_quantum >= self.quantum_length:
            self._interrupt_queue.append(Interrupt(InterruptType.TIMER, self.active_process.pid))

    def _handle_interrupts(self):
        for interrupt in self._interrupt_queue:
            if self.active_process and self.active_process.pid == interrupt.process_id:
                self.active_process = None

            if interrupt.type == InterruptType.TIMER:
                self.regulator.handle_timer_interrupt(interrupt.process_id)
            elif interrupt.type == InterruptType.IO_DONE:
                self.regulator.handle_io_done_interrupt(interrupt.process_id)
            elif interrupt.type == InterruptType.PROCESS_EXIT:
                self.regulator.handle_exit_interrupt(interrupt.process_id)

        self._interrupt_queue.clear()

    def _generate_new_task(self) -> None:
        if self.process_manager.is_table_full():
            self.next_task_to_load = None
            return

        task_params = self.config_loader.get_new_task_params()

        new_task = Process(
            size=task_params['process_size'],
            program_length=task_params['program_length'],
            creation_tick=self.system_tick,
            io_probability=task_params['io_command_probability']
        )
        self.next_task_to_load = new_task

    def _load_next_task(self) -> bool:
        task_to_load = self.next_task_to_load
        if not task_to_load:
            return False
        if self.process_manager.is_table_full():
            return False
        if not self.memory_manager.has_enough_space(task_to_load.size):
            return False

        task_to_load.state = ProcessState.LOADING
        self.process_manager.register_process(task_to_load)
        self.memory_manager.allocate(task_to_load.pid, task_to_load.size)
        self.regulator._ready_queue.add_process(task_to_load)
        task_to_load.state = ProcessState.READY
        self.next_task_to_load = None
        return True

    def create_new_process(self, size: int) -> str:
        if not self.memory_manager.has_enough_space(size):
            return f"Ошибка: Недостаточно памяти."
        task_params = self.config_loader.get_new_task_params()
        new_process = self.process_manager.create_and_register_process(
            size=size,
            program_length=task_params['program_length'],
            creation_tick=self.system_tick,
            io_probability=task_params['io_command_probability']
        )
        if new_process is None:
            return "Ошибка: Таблица процессов заполнена."
        if not self.memory_manager.allocate(new_process.pid, new_process.size):
            self.process_manager.remove_process(new_process.pid)
            return "Ошибка: Не удалось выделить память."

        self.regulator._ready_queue.add_process(new_process)
        new_process.state = ProcessState.READY
        return f"Процесс {new_process.pid} успешно создан вручную."

    def get_system_stats(self) -> Dict:
        all_processes = list(self.process_manager.process_table.values())
        cpu_state = "Работа" if self.active_process else "Ожидание"
        last_command_obj = self.cpu.last_executed_command
        last_command_str = str(last_command_obj) if last_command_obj else "N/A"

        stats = {
            "system_tick": self.system_tick,
            "speed_hz": round(self.speed_hz, 2),
            "memory_usage": f"{self.memory_manager.used_memory}/{self.memory_manager.total_size}",
            "cpu_state": cpu_state,
            "active_pid": self.active_process.pid if self.active_process else "N/A",
            "last_command": last_command_str,
            "next_task": self.next_task_to_load,
            "process_count": f"{len(self.process_manager.process_table)}/{self.process_manager.max_processes}",
            "ready_count": len(self.scheduler.ready_queue),
            "blocked_count": len(self.blocked_queue),
            "all_processes": all_processes,
            "execution_history": list(self.execution_history),
            "avg_wait_time": self.stats_manager.get_average_wait_time(),
            "avg_turnaround_time": self.stats_manager.get_average_turnaround_time(),
            "completed_count": self.stats_manager.get_completed_processes_count(),
            "avg_mono_time": self.stats_manager.get_average_mono_time(),
            "performance_ratio": self.stats_manager.get_performance_ratio(),
            "last_process_report": self.stats_manager.get_last_process_report()
        }
        return stats

    def change_speed(self, factor: float):
        new_speed = self.speed_hz * factor
        self.speed_hz = max(0.1, min(1000.0, new_speed))
