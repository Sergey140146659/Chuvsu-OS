import time
from typing import Dict, Optional

from .core.cpu import CPU
from .core.memory import MemoryManager
from .core.process import Process
from .services.process_manager import ProcessManager
from .services.scheduler import Scheduler
class OperatingSystem:

    def __init__(self, config: Dict):
        self.cpu = CPU()
        self.memory_manager = MemoryManager(total_size=config['memory'])
        self.process_manager = ProcessManager(max_processes=config['max_processes'])
        self.scheduler = Scheduler()
        self.default_process_size: int = config.get('default_process_size', 128)
        self.next_task_to_load: Optional[Process] = None
        self.speed_hz: float = config.get('initial_speed_hz', 1.0)
        self._running: bool = False

    def _generate_new_task(self) -> None:
        if self.process_manager.is_table_full():
            self.next_task_to_load = None
            return

        new_task = Process(size=self.default_process_size)
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
            process_to_run = self.scheduler.get_next_process()

            if process_to_run:
                self.cpu.execute(process_to_run)

            if self.speed_hz > 0:
                time.sleep(1.0 / self.speed_hz)
            else:
                time.sleep(0.1)


    def create_new_process(self, size: int) -> str:
        if self.process_manager.is_table_full():
            return "Ошибка: Таблица процессов заполнена."

        if not self.memory_manager.has_enough_space(size):
            return f"Ошибка: Недостаточно памяти. Требуется {size}, доступно {self.memory_manager.total_size - self.memory_manager.used_memory}."

        new_process = self.process_manager.create_and_register_process(size)
        if new_process is None:
            return "Ошибка: Не удалось создать процесс."

        if not self.memory_manager.allocate(new_process.pid, new_process.size):
            self.process_manager.remove_process(new_process.pid)
            return "Ошибка: Не удалось выделить память."

        self.scheduler.add_process(new_process)

        return f"Процесс {new_process.pid} успешно создан."


    def get_system_stats(self) -> Dict:
        all_processes = list(self.process_manager.process_table.values())

        stats = {
            "speed_hz": round(self.speed_hz, 2),
            "memory_usage": f"{self.memory_manager.used_memory}/{self.memory_manager.total_size}",
            "process_count": f"{len(self.process_manager.process_table)}/{self.process_manager.max_processes}",
            "all_processes": all_processes,
            "next_task": self.next_task_to_load
        }
        return stats

    def change_speed(self, factor: float):
        new_speed = self.speed_hz * factor
        self.speed_hz = max(0.1, min(1000.0, new_speed))
