from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ProbeEvent:
    operation: str
    key: str
    h1: int
    probe_path: List[int]
    final_slot: Optional[int]
    is_collision: bool
    steps: int


class LoggedHashTable:
    """Wrapper: bọc ngoài bất kỳ HashTableBase nào, ghi lại events"""

    def __init__(self, strategy_class, size=11):
        self._ht = strategy_class(size)
        self.events: List[ProbeEvent] = []
        self.collision_count = 0

    @property
    def table(self):
        return self._ht.table

    @property
    def size(self):
        return self._ht.size

    @property
    def load_factor(self):
        return self._ht.load_factor

    def insert(self, key, value):
        h1 = self._ht.hash1(key)
        probe_path = self._compute_probe_path(key)
        is_col = len(probe_path) > 1

        if is_col:
            self.collision_count += 1

        self._ht.insert(key, value)

        event = ProbeEvent(
            operation="insert", key=str(key), h1=h1,
            probe_path=probe_path,
            final_slot=probe_path[-1] if probe_path else h1,
            is_collision=is_col,
            steps=len(probe_path)
        )
        self.events.append(event)
        return event

    def _compute_probe_path(self, key):
        from core.hash_table import (
            ChainingHashTable,
            LinearProbingHashTable,
            QuadraticProbingHashTable,
            DoubleHashingHashTable
        )

        h1 = self._ht.hash1(key)
        path = []

        if isinstance(self._ht, ChainingHashTable):
            return [h1]

        elif isinstance(self._ht, DoubleHashingHashTable):
            h2 = self._ht.hash2(key)
            for i in range(self._ht.size):
                slot = (h1 + i * h2) % self._ht.size
                path.append(slot)
                if self._ht.table[slot] is None or \
                   self._ht.table[slot] is self._ht.DELETED:
                    break

        elif isinstance(self._ht, QuadraticProbingHashTable):
            for i in range(self._ht.size):
                slot = (h1 + i * i) % self._ht.size
                path.append(slot)
                if self._ht.table[slot] is None or \
                   self._ht.table[slot] is self._ht.DELETED:
                    break

        else:  # Linear Probing
            for i in range(self._ht.size):
                slot = (h1 + i) % self._ht.size
                path.append(slot)
                if self._ht.table[slot] is None or \
                   self._ht.table[slot] is self._ht.DELETED:
                    break

        return path

    def get_stats(self):
        return {
            "load_factor": round(self.load_factor, 3),
            "collision_count": self.collision_count,
            "total_ops": len(self.events),
            "avg_probe_len": round(
                sum(e.steps for e in self.events) / len(self.events), 2
            ) if self.events else 0
        }