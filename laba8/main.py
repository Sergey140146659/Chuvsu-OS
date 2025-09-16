import random

from src.config_loader import ConfigLoader
from src.os import OperatingSystem
from src.ui import CLI


def main():
    print("Инициализация эмулятора...")
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)
    print(f"Генератор случайных чисел инициализирован с сидом: {RANDOM_SEED}")
    config_loader = ConfigLoader(filepath="parameters.json")
    system_config = config_loader.get_system_config()
    print("Сгенерированы системные параметры:")
    for key, value in system_config.items():
        print(f"  - {key}: {value}")
    os_emulator = OperatingSystem(
        system_config=system_config,
        config_loader=config_loader
    )
    cli = CLI(os_emulator)
    print("\nЗапуск интерфейса. Введите 'help' для списка команд.")
    cli.start()
    print("Эмулятор завершил свою работу.")

if __name__ == "__main__":
    main()
