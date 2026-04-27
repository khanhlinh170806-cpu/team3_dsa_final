"""
Separate Chaining — each bucket holds a list of (key, value) pairs.

Time complexity (average):
  - Insert : O(1)
  - Search : O(1)
  - Delete : O(1)

Worst case (all keys hash to same bucket): O(n)
"""
from .base_hash_table import BaseHashTable


class ChainingHashTable(BaseHashTable):
    """
    Hash table using Separate Chaining for collision resolution.

    Each slot in the internal array holds a Python list (bucket) of
    (key, value) tuples.  Collisions are handled by appending to the
    bucket list rather than probing.
    """

    def __init__(self, capacity: int = 16, load_factor_threshold: float = 0.75):
        super().__init__(capacity, load_factor_threshold)
        # Override: every slot is an empty list (bucket)
        self._table = [[] for _ in range(self.capacity)]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_in_bucket(self, bucket: list, key):
        """Return (index, value) inside a bucket, or (-1, None)."""
        for i, (k, v) in enumerate(bucket):
            if k == key:
                return i, v
        return -1, None

    # ------------------------------------------------------------------
    # Resize support
    # ------------------------------------------------------------------

    def _resize(self):
        """Override to properly rebuild list-of-lists structure."""
        old_table = self._table
        self.capacity *= 2
        self._table = [[] for _ in range(self.capacity)]
        self.size = 0
        self._collision_count = 0

        for bucket in old_table:
            for key, value in bucket:
                self._insert_no_resize(key, value)

    def _insert_no_resize(self, key, value):
        """Insert without triggering another resize (used during rehash)."""
        index = self._hash1(key)
        bucket = self._table[index]
        i, _ = self._find_in_bucket(bucket, key)
        if i == -1:
            if bucket:               # bucket already has items → collision
                self._collision_count += 1
            bucket.append((key, value))
            self.size += 1
        else:
            bucket[i] = (key, value)

    def _rehash_entry(self, entry):
        """Required by base class; not used because we override _resize."""
        pass

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def insert(self, key, value) -> None:
        """
        Insert or update key-value pair.

        If the load factor exceeds the threshold, the table is resized
        before inserting.
        """
        if self._should_resize():
            self._resize()

        index = self._hash1(key)
        bucket = self._table[index]
        i, _ = self._find_in_bucket(bucket, key)

        if i == -1:
            if bucket:               # non-empty bucket → collision
                self._collision_count += 1
            bucket.append((key, value))
            self.size += 1
        else:
            bucket[i] = (key, value)   # update existing key

    def search(self, key):
        """
        Return the value associated with key, or None if not found.
        """
        index = self._hash1(key)
        bucket = self._table[index]
        _, value = self._find_in_bucket(bucket, key)
        return value

    def delete(self, key) -> bool:
        """
        Remove key from the table.  Returns True on success.
        """
        index = self._hash1(key)
        bucket = self._table[index]
        i, _ = self._find_in_bucket(bucket, key)

        if i == -1:
            return False

        bucket.pop(i)
        self.size -= 1
        return True

    # ------------------------------------------------------------------
    # Extras
    # ------------------------------------------------------------------

    def keys(self):
        for bucket in self._table:
            for k, _ in bucket:
                yield k

    def values(self):
        for bucket in self._table:
            for _, v in bucket:
                yield v

    def items(self):
        for bucket in self._table:
            yield from bucket

    def __iter__(self):
        return self.keys()

    def visualize(self) -> str:
        """Return an ASCII visualization of the bucket structure."""
        lines = [f"ChainingHashTable (capacity={self.capacity}):"]
        for i, bucket in enumerate(self._table):
            if bucket:
                chain = " -> ".join(f"({k!r}: {v!r})" for k, v in bucket)
                lines.append(f"  [{i:3d}] {chain}")
        return "\n".join(lines)