# laba1/src/ui.py

import os
import time
import threading
from .os import OperatingSystem

class CLI:
    """Управляет пользовательским интерфейсом в консоли."""
    def __init__(self, os_instance: OperatingSystem):
        self.os = os_instance
        self._running = True

    def _display_stats(self):
        """Отображает текущую статистику системы."""
        stats = self.os.get_system_stats()
        
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("--- Эмулятор Операционной Системы ---")
        print(f"Скорость: {stats['speed_hz']} такт/сек | Память: {stats['memory_usage']} | Процессы: {stats['process_count']}")
        print("--- Активный процесс ---")
        print(f"PID: {stats['active_pid']} | Счетчик команд (PC): {stats['active_pc']}")
        print(f"--- Готовые процессы (PID): {stats['ready_pids']} ---")
        print("-" * 39)
        print("Ожидание команды... (введите 'help' для справки или 'exit' для выхода)")

    def _handle_command(self, command_line: str):
        """Парсит и обрабатывает одну команду."""
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
        """Запускает UI и основной цикл обработки команд."""
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

