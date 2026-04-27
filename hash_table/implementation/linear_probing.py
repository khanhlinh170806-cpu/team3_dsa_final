"""
Linear Probing — Open Addressing variant.

Probe sequence:  h(k, i) = (h1(k) + i) % capacity   for i = 0, 1, 2, …

Time complexity (average, good load factor α < 0.7):
  - Insert : O(1 / (1-α))   → O(1) amortized
  - Search : O(1 / (1-α))
  - Delete : O(1 / (1-α))

Issues:
  - Primary clustering: consecutive filled slots slow down future probes.
  - Delete cannot simply set slot to None → use TOMBSTONE sentinel.
"""
from .base_hash_table import BaseHashTable

# Sentinel object to mark deleted slots ("tombstone")
_DELETED = object()


class LinearProbingHashTable(BaseHashTable):
    """
    Hash table using Linear Probing (Open Addressing).

    Each slot holds either:
      - None      : empty, never used
      - _DELETED  : tombstone (deleted key; probing continues past it)
      - (key, val): live entry
    """

    def __init__(self, capacity: int = 16, load_factor_threshold: float = 0.70):
        super().__init__(capacity, load_factor_threshold)
        # _table already initialised to [None]*capacity by parent

    # ------------------------------------------------------------------
    # Probe helper
    # ------------------------------------------------------------------

    def _probe(self, key):
        """
        Generator that yields slot indices in linear probe order.
        Stops after a full scan (capacity steps) to avoid infinite loops.
        """
        start = self._hash1(key)
        for i in range(self.capacity):
            yield (start + i) % self.capacity

    # ------------------------------------------------------------------
    # Resize support
    # ------------------------------------------------------------------

    def _rehash_entry(self, entry):
        """Re-insert one (key, value) tuple into the resized table."""
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
        """
        Insert or update key-value pair using linear probing.

        We track the first tombstone encountered so we can reuse the slot
        when inserting a new key (avoids unnecessary growth).
        """
        if self._should_resize():
            self._resize()

        first_tombstone = None

        for idx in self._probe(key):
            slot = self._table[idx]

            if slot is None:
                # Empty slot — insert here (or at tombstone if found earlier)
                target = first_tombstone if first_tombstone is not None else idx
                self._table[target] = (key, value)
                self.size += 1
                return

            if slot is _DELETED:
                if first_tombstone is None:
                    first_tombstone = idx
                # Continue probing to check for existing key

            elif slot[0] == key:
                # Found existing key → update value in place
                self._table[idx] = (key, value)
                return

            else:
                self._collision_count += 1  # probe step over live entry

        # Table full (all slots probed) — should not happen with resizing
        if first_tombstone is not None:
            self._table[first_tombstone] = (key, value)
            self.size += 1
        else:
            raise RuntimeError("Hash table is full — resizing failed.")

    def search(self, key):
        """
        Return value for key, or None if not found.
        Stops at an empty (None) slot because a key cannot exist past it.
        """
        for idx in self._probe(key):
            slot = self._table[idx]

            if slot is None:
                return None          # Empty slot terminates search

            if slot is _DELETED:
                continue             # Tombstone — keep probing

            if slot[0] == key:
                return slot[1]

        return None

    def delete(self, key) -> bool:
        """
        Mark the slot as TOMBSTONE instead of setting to None.
        This preserves probe chains for other keys.
        """
        for idx in self._probe(key):
            slot = self._table[idx]

            if slot is None:
                return False         # Key definitely not present

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
        """Return ASCII layout of the internal array."""
        lines = [f"LinearProbingHashTable (capacity={self.capacity}):"]
        for i, slot in enumerate(self._table):
            if slot is None:
                marker = "None"
            elif slot is _DELETED:
                marker = "<DELETED>"
            else:
                marker = f"({slot[0]!r}: {slot[1]!r})"
            lines.append(f"  [{i:3d}] {marker}")
        return "\n".join(lines)