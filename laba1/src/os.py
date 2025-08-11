# laba1/src/os.py

import time
from typing import Dict

from .core.cpu import CPU
from .core.memory import MemoryManager
from .services.process_manager import ProcessManager
from .services.scheduler import Scheduler

class OperatingSystem:
    """Главный класс, эмулирующий работу операционной системы."""

    def __init__(self, config: Dict):
        self.cpu = CPU()
        self.memory_manager = MemoryManager(total_size=config['memory'])
        self.process_manager = ProcessManager(max_processes=config['max_processes'])
        self.scheduler = Scheduler()

        self.speed_hz: float = config.get('initial_speed_hz', 1.0)
        self._running: bool = False

    def boot(self):
        """Запускает операционную систему и основной цикл."""
        self._running = True
        self.run()

    def shutdown(self):
        """Останавливает операционную систему."""
        self._running = False

    def run(self):
        """Основной цикл (сердцебиение) операционной системы."""
        while self._running:
            process_to_run = self.scheduler.get_next_process()

            if process_to_run:
                self.cpu.execute(process_to_run)

            if self.speed_hz > 0:
                time.sleep(1.0 / self.speed_hz)
            else:
                time.sleep(0.1)


    def create_new_process(self, size: int) -> str:
        """
        Координирует создание нового процесса.
        Возвращает сообщение о статусе операции.
        """
        if self.process_manager.is_table_full():
            return "Ошибка: Таблица процессов заполнена."

        if not self.memory_manager.has_enough_space(size):
            return f"Ошибка: Недостаточно памяти. Требуется {size}, доступно {self.memory_manager.total_size - self.memory_manager.used_memory}."

        new_process = self.process_manager.create_process(size)
        if new_process is None:
            return "Ошибка: Не удалось создать процесс."

        if not self.memory_manager.allocate(new_process.pid, new_process.size):
            self.process_manager.remove_process(new_process.pid)
            return "Ошибка: Не удалось выделить память."

        self.scheduler.add_process(new_process)

        return f"Процесс {new_process.pid} успешно создан."


    def get_system_stats(self) -> Dict:
        """Собирает статистику из разных компонентов для отображения."""
        active_process = self.scheduler.get_next_process()
        
        stats = {
            "speed_hz": round(self.speed_hz, 2),
            "memory_usage": f"{self.memory_manager.used_memory}/{self.memory_manager.total_size}",
            "process_count": f"{len(self.process_manager.process_table)}/{self.process_manager.max_processes}",
            "active_pid": active_process.pid if active_process else "N/A",
            "active_pc": active_process.program_counter if active_process else "N/A",
            "ready_pids": [p.pid for p in self.scheduler.ready_queue]
        }
        return stats

    def change_speed(self, factor: float):
        """Изменяет скорость симуляции (увеличивает или уменьшает)."""
        new_speed = self.speed_hz * factor
        self.speed_hz = max(0.1, min(1000.0, new_speed))

