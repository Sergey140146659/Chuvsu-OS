import os
import threading
from .os import OperatingSystem
import time

class CLI:
    def __init__(self, os_instance: OperatingSystem):
        self.os = os_instance
        self._running = True

    def _display_stats(self, stats):
        os.system('cls' if os.name == 'nt' else 'clear')
        self._display_header()
        self._display_system_info(stats)
        self._display_cpu_info(stats)
        self._display_process_table(stats)
        self._display_execution_history(stats)
        self._display_average_stats(stats)
        self._display_footer()


    def _display_header(self):
        print("--- Эмулятор Операционной Системы (Лаб. 6) ---")

    def _display_system_info(self, stats):
        print("\n[Параметры Системы]")
        print(f"  Время: {stats['system_tick']} такт | Скорость: {stats['speed_hz']} такт/сек")
        print(f"  Память: {stats['memory_usage']} | Процессы: {stats['process_count']} (Готовых: {stats['ready_count']}, Заблокировано: {stats['blocked_count']})")
        if stats['next_task']:
            print(f"  Новое задание на загрузку: {stats['next_task']}")
        else:
            print("  Новое задание на загрузку: не сгенерировано")

    def _display_cpu_info(self, stats):
        print("\n[Параметры CPU]")
        print(f"  Состояние: {stats['cpu_state']} | Активный PID: {stats['active_pid']} | Последняя команда: {stats['last_command']}")

    def _display_process_table(self, stats):
        print("\n[Таблица Процессов (PSW)]")
        header = f"{'PID':<5} | {'Состояние':<12} | {'PC':<7} | {'Тики':<5} | {'I/O':<5} | {'Время ожидания':<15} | {'Размер':<7}"
        print(header)
        print("-" * len(header))

        if stats['all_processes']:
            sorted_processes = sorted(stats['all_processes'], key=lambda p: p.pid)
            for proc in sorted_processes:
                print(f"{proc.pid:<5} | {proc.state.value:<12} | {proc.program_counter:<7} | {proc.ticks_worked_in_quantum:<5} | {proc.io_time_remaining:<5} | {proc.wait_time:<15} | {proc.size:<7}")
        else:
            print("В системе нет процессов.")

    def _display_execution_history(self, stats):
        print("\n[История выполнения на CPU (последние 16)]")
        history_str = ' -> '.join(map(str, stats['execution_history']))
        print(f"  {history_str}")

    def _display_average_stats(self, stats):
        print("\n[Статистика по завершенным процессам]")
        print(f"  Всего завершено: {stats['completed_count']}")
        print(f"  Среднее время ожидания: {stats['avg_wait_time']:.2f} тактов")
        print(f"  Среднее время выполнения (Turnaround): {stats['avg_turnaround_time']:.2f} тактов")

    def _display_footer(self):
        print("\n" + "="*80)
        print("Ожидание команды... (введите 'help' для справки или 'exit' для выхода)")

    def start(self):
        os_thread = threading.Thread(target=self.os.boot, name="OSThread")
        os_thread.daemon = True
        os_thread.start()

        self._display_stats(self.os.get_system_stats())
        while self._running:
            try:
                command = input()
                self._handle_command(command)
            except (KeyboardInterrupt, EOFError):
                self.stop()

    def _handle_command(self, command_line: str):
        parts = command_line.strip().lower().split()
        if not parts:
            self._display_stats(self.os.get_system_stats())
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
                  "  exit          - Завершить работу эмулятора.\n")
            input("Нажмите Enter для продолжения...")

        elif command == "create" and len(parts) > 1:
            try:
                size = int(parts[1])
                result = self.os.create_new_process(size)
                input(f"\n> {result}\n\nНажмите Enter для продолжения...")
            except ValueError:
                input("\n> Ошибка: размер должен быть целым числом.\n\nНажмите Enter...")

        elif command.startswith("speed+"):
            self._change_speed_handler(command, increase=True)
        elif command.startswith("speed-"):
            self._change_speed_handler(command, increase=False)

        else:
            print(f"\n> Неизвестная команда: '{command}'. Введите 'help' для справки.")
            time.sleep(1.5)


        self._display_stats(self.os.get_system_stats())


    def _change_speed_handler(self, command: str, increase: bool):
        try:
            op = "speed+" if increase else "speed-"
            val_str = command.replace(op, "").replace("%", "")
            percentage = int(val_str)
            factor = (1 + percentage / 100.0) if increase else (1 - percentage / 100.0)
            self.os.change_speed(factor)
        except (ValueError, IndexError):
            print(f"\n> Ошибка формата. Используйте: speed+/-<N>% (например, speed+10%)")
            time.sleep(1.5)


    def stop(self):
        if self._running:
            self._running = False
            self.os.shutdown()
