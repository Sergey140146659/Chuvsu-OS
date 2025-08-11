# laba1/src/core/memory.py

from typing import Dict

class MemoryManager:
    """Управляет распределением памяти в системе."""

    def __init__(self, total_size: int):
        self.total_size: int = total_size
        self.used_memory: int = 0
        self.allocated_blocks: Dict[int, int] = {}

    def has_enough_space(self, size: int) -> bool:
        """Проверяет, достаточно ли свободной памяти для выделения."""
        return self.total_size - self.used_memory >= size

    def allocate(self, pid: int, size: int) -> bool:
        """Выделяет память для процесса, если есть место."""
        if pid in self.allocated_blocks:
            return False

        if not self.has_enough_space(size):
            return False

        self.used_memory += size
        self.allocated_blocks[pid] = size
        return True

    def free(self, pid: int) -> bool:
        """Освобождает память, выделенную для процесса."""
        if pid not in self.allocated_blocks:
            return False

        size_to_free = self.allocated_blocks.pop(pid)
        self.used_memory -= size_to_free
        return True

    def __repr__(self) -> str:
        """Возвращает строковое представление для отладки."""
        return f"MemoryManager(used={self.used_memory}/{self.total_size})"

