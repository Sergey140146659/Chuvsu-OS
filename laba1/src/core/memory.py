from typing import Dict

class MemoryManager:
    def __init__(self, total_size: int):
        self.total_size: int = total_size
        self.used_memory: int = 0
        self.allocated_blocks: Dict[int, int] = {}

    def has_enough_space(self, size: int) -> bool:
        return self.total_size - self.used_memory >= size

    def allocate(self, pid: int, size: int) -> bool:
        if pid in self.allocated_blocks:
            return False

        if not self.has_enough_space(size):
            return False

        self.used_memory += size
        self.allocated_blocks[pid] = size
        return True

    def free(self, pid: int) -> bool:
        if pid not in self.allocated_blocks:
            return False

        size_to_free = self.allocated_blocks.pop(pid)
        self.used_memory -= size_to_free
        return True

    def __repr__(self) -> str:
        return f"MemoryManager(used={self.used_memory}/{self.total_size})"
