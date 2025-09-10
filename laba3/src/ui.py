import os
import time
import threading
from .os import OperatingSystem

class CLI:
    def __init__(self, os_instance: OperatingSystem):
        self.os = os_instance
        self._running = True

    def _display_stats(self):
        stats = self.os.get_system_stats()

        os.system('cls' if os.name == 'nt' else 'clear')

        print("--- Эмулятор Операционной Системы (Лаб. 3) ---")
        print(f"CPU: {stats['cpu_state']} | Активный PID: {stats['active_pid']} | Скорость: {stats['speed_hz']} такт/сек")
        print(f"Память: {stats['memory_usage']} | Процессы: {stats['process_count']}")

        print("\n--- Таблица Процессов (PSW) ---")
        print(f"{'PID':<5} | {'Состояние':<12} | {'PC':<7} | {'Тики':<5} | {'Размер':<7}")
        print("-" * 55)

        if stats['all_processes']:
            sorted_processes = sorted(stats['all_processes'], key=lambda p: p.pid)
            for proc in sorted_processes:
                pid_str = str(proc.pid)
                state_str = proc.state.value
                pc_str = str(proc.program_counter)
                ticks_str = str(proc.ticks_worked_in_quantum)
                size_str = str(proc.size)
                print(f"{pid_str:<5} | {state_str:<12} | {pc_str:<7} | {ticks_str:<5} | {size_str:<7}")
        else:
            print("В системе нет процессов.")

        print("-" * 55)

        if stats['next_task']:
            print(f"Следующее задание на загрузку: {stats['next_task']}")
        else:
            print("Следующее задание на загрузку: не сгенерировано.")
        print("\nОжидание команды... (введите 'help' для справки или 'exit' для выхода)")

    def _handle_command(self, command_line: str):
        parts = command_line.strip().lower().split()
        if not parts:
            return

        command = parts[0]

        if command == "exit":
            self.stop()
            return

        elif command == "help" or command == "/?":
            print("\nДоступные команды:\n"
                  "  create <size> - Создать процесс с размером <size> (целое число).\n"
                  "  speed+<N>%    - Увеличить скорость на N процентов (например, speed+10%).\n"
                  "  speed-<N>%    - Уменьшить скорость на N процентов (например, speed-5%).\n"
                  "  exit          - Завершить работу эмулятора.\n"
                  "  <любая другая команда или Enter> - обновить статистику.\n")
            input("Нажмите Enter для продолжения...")

        elif command == "create" and len(parts) > 1:
            try:
                size = int(parts[1])
                result = self.os.create_new_process(size)
                # Выведем результат в отдельном окне, чтобы было видно
                input(f"\n> {result}\n\nНажмите Enter для продолжения...")
            except ValueError:
                input("\n> Ошибка: размер должен быть целым числом.\n\nНажмите Enter...")

        elif command.startswith("speed+"):
            self._change_speed_handler(command, increase=True)
        elif command.startswith("speed-"):
            self._change_speed_handler(command, increase=False)

        self._display_stats()

    def _change_speed_handler(self, command: str, increase: bool):
        try:
            op = "speed+" if increase else "speed-"
            val_str = command.replace(op, "").replace("%", "")
            percentage = int(val_str)
            factor = (1 + percentage / 100.0) if increase else (1 - percentage / 100.0)
            self.os.change_speed(factor)
        except (ValueError, IndexError):
            input(f"\n> Ошибка формата. Используйте: speed+/-<N>%.\n\nНажмите Enter...")

    def start(self):
        os_thread = threading.Thread(target=self.os.boot, name="OSThread")
        os_thread.daemon = True
        os_thread.start()

        self._display_stats()
        while self._running:
            try:
                command = input()
                self._handle_command(command)
            except (KeyboardInterrupt, EOFError):
                self.stop()

    def stop(self):
        if self._running:
            self._running = False
            self.os.shutdown()
