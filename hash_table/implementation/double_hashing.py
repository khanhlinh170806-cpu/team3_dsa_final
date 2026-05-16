"""
Double Hashing — Open Addressing variant.

Probe sequence:  h(k, i) = (h1(k) + i * h2(k)) % capacity

Where:
  h1(k) = hash(k) % capacity         (primary hash)
  h2(k) = p - (hash(k) % p)          (secondary hash, p = largest prime < capacity)

Why it's better:
  - Eliminates both primary AND secondary clustering.
  - Each key gets a unique step size (h2(k)), so probe sequences are
    effectively independent.

Requirement:
  - h2(k) must never be 0 (would create an infinite loop at h1(k)).
  - h2(k) and capacity must be co-prime (guaranteed when capacity is a
    power of 2 and h2 returns an odd number, or when p is prime and
    capacity is not a multiple of p).
"""
from .base_hash_table import BaseHashTable

_DELETED = object()


class DoubleHashingHashTable(BaseHashTable):
    """
    Hash table using Double Hashing (Open Addressing).

    Probe: (h1(key) + i * h2(key)) % capacity  for i = 0, 1, 2, …
    """

    # ── Public sentinel — dùng bởi logger.py ──────────────────────────
    DELETED = _DELETED

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, capacity: int = 16, load_factor_threshold: float = 0.65):
        super().__init__(capacity, load_factor_threshold)

    # ------------------------------------------------------------------
    # Public properties — logger.py cần truy cập qua tên public
    # ------------------------------------------------------------------

    @property
    def table(self):
        """Expose internal _table dưới tên public."""
        return self._table

    # ------------------------------------------------------------------
    # Hash Functions (public alias để logger.py gọi được)
    # ------------------------------------------------------------------

    def hash1(self, key) -> int:
        """Public alias của _hash1 — dùng bởi LoggedHashTable."""
        return self._hash1(key)

    def hash2(self, key) -> int:
        """Public alias của _hash2 — dùng bởi LoggedHashTable."""
        return self._hash2(key)

    def _hash1(self, key) -> int:
        return hash(key) % self.capacity

    def _hash2(self, key) -> int:
        """
        Hàm băm thứ hai quyết định 'bước nhảy' (step size).
        Để đảm bảo duyệt hết bảng khi capacity là lũy thừa của 2,
        bước nhảy PHẢI là số lẻ.
        """
        h = hash(key)
        step = (h % (self.capacity - 1))
        return (step if step > 0 else 1) | 1

    # ------------------------------------------------------------------
    # Probe helper
    # ------------------------------------------------------------------

    def _probe(self, key):
        """
        Yield slot indices using double hashing probe order.
        h2(key) is non-zero by construction.
        """
        h1 = self._hash1(key)
        h2 = self._hash2(key)

        for i in range(self.capacity):
            yield (h1 + i * h2) % self.capacity

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
            raise RuntimeError("Double hashing failed to find an open slot.")

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
        lines = [f"DoubleHashingHashTable (capacity={self.capacity}):"]
        for i, slot in enumerate(self._table):
            if slot is None:
                marker = "None"
            elif slot is _DELETED:
                marker = "<DELETED>"
            else:
                marker = f"({slot[0]!r}: {slot[1]!r})"
            lines.append(f"  [{i:3d}] {marker}")
        return "\n".join(lines)