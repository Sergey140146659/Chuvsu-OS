# laba1/main.py

import json
import os
from src.os import OperatingSystem
from src.ui import CLI

def load_config(path: str = "config.json") -> dict:
    """Загружает конфигурацию из JSON-файла."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, path)
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации не найден по пути {config_path}")
        return {"memory": 1024, "max_processes": 10, "initial_speed_hz": 1.0}
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {config_path}")
        return {"memory": 1024, "max_processes": 10, "initial_speed_hz": 1.0}


def main():
    """Основная функция для запуска эмулятора ОС."""
    print("Инициализация эмулятора...")
    
    config = load_config()
    os_emulator = OperatingSystem(config)
    cli = CLI(os_emulator)
    print("Запуск интерфейса. Введите 'help' для списка команд.")
    cli.start()
    print("Эмулятор завершил свою работу.")

if __name__ == "__main__":
    main()

