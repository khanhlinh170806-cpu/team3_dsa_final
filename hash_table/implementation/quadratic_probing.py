"""
Quadratic Probing — Open Addressing variant.

Probe sequence:  h(k, i) = (h1(k) + c1*i + c2*i²) % capacity

Using c1=0, c2=1  →  h(k, i) = (h1(k) + i²) % capacity

Advantage over Linear Probing:
  - Reduces *primary clustering* (consecutive slots all slowing each other).

New problem:
  - *Secondary clustering*: two keys with the same initial hash follow the
    same probe sequence.

Guarantee for full table coverage:
  - Capacity must be a prime number, or a power of 2 with c1=0.5, c2=0.5.
  - We use power-of-2 capacity (doubled on resize) — safe with i²/2 formula.
"""
from .base_hash_table import BaseHashTable

_DELETED = object()


class QuadraticProbingHashTable(BaseHashTable):
    """
    Hash table using Quadratic Probing (Open Addressing).

    Probe: (h1(key) + i²) % capacity  for i = 0, 1, 2, …
    """

    def __init__(self, capacity: int = 16, load_factor_threshold: float = 0.60):
        # Keep load factor lower than linear probing to guarantee full scan
        super().__init__(capacity, load_factor_threshold)

    # ------------------------------------------------------------------
    # Probe helper
    # ------------------------------------------------------------------

    def _probe(self, key):
        """
        Yield slot indices in quadratic probe order.
        Iterates up to capacity/2 steps (sufficient for power-of-2 tables).
        """
        start = self._hash1(key)
        for i in range(self.capacity):
            yield (start + i * i) % self.capacity

    # ------------------------------------------------------------------
    # Resize support
    # ------------------------------------------------------------------

    def _rehash_entry(self, entry):
        if entry is not None and entry is not _DELETED:
            self.insert(entry[0], entry[1])

    def _resize(self):
        old_table = self._table
        self.capacity *= 2
        self._table = [None] * self.capacity
        self.size = 0
        self._collision_count = 0
        for entry in old_table:
            if entry is not None and entry is not _DELETED:
                self._rehash_entry(entry)

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def insert(self, key, value) -> None:
        if self._should_resize():
            self._resize()

        first_tombstone = None

        for idx in self._probe(key):
            slot = self._table[idx]

            if slot is None:
                target = first_tombstone if first_tombstone is not None else idx
                self._table[target] = (key, value)
                self.size += 1
                return

            if slot is _DELETED:
                if first_tombstone is None:
                    first_tombstone = idx

            elif slot[0] == key:
                self._table[idx] = (key, value)
                return

            else:
                self._collision_count += 1

        if first_tombstone is not None:
            self._table[first_tombstone] = (key, value)
            self.size += 1
        else:
            raise RuntimeError("Quadratic probing failed to find an open slot.")

    def search(self, key):
        for idx in self._probe(key):
            slot = self._table[idx]

            if slot is None:
                return None

            if slot is _DELETED:
                continue

            if slot[0] == key:
                return slot[1]

        return None

    def delete(self, key) -> bool:
        for idx in self._probe(key):
            slot = self._table[idx]

            if slot is None:
                return False

            if slot is _DELETED:
                continue

            if slot[0] == key:
                self._table[idx] = _DELETED
                self.size -= 1
                return True

        return False

    # ------------------------------------------------------------------
    # Extras
    # ------------------------------------------------------------------

    def keys(self):
        for slot in self._table:
            if slot is not None and slot is not _DELETED:
                yield slot[0]

    def values(self):
        for slot in self._table:
            if slot is not None and slot is not _DELETED:
                yield slot[1]

    def items(self):
        for slot in self._table:
            if slot is not None and slot is not _DELETED:
                yield slot

    def __iter__(self):
        return self.keys()

    def visualize(self) -> str:
        lines = [f"QuadraticProbingHashTable (capacity={self.capacity}):"]
        for i, slot in enumerate(self._table):
            if slot is None:
                marker = "None"
            elif slot is _DELETED:
                marker = "<DELETED>"
            else:
                marker = f"({slot[0]!r}: {slot[1]!r})"
            lines.append(f"  [{i:3d}] {marker}")
        return "\n".join(lines)