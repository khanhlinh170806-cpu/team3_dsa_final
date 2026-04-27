"""
Base Hash Table - Abstract base class for all collision resolution strategies.
"""
from abc import ABC, abstractmethod


class BaseHashTable(ABC):
    """
    Abstract base class for hash table implementations.
    Defines the common interface and shared utilities.
    """

    def __init__(self, capacity: int = 16, load_factor_threshold: float = 0.75):
        self.capacity = capacity
        self.load_factor_threshold = load_factor_threshold
        self.size = 0
        self._table = [None] * self.capacity
        self._collision_count = 0  # for benchmarking

    # ------------------------------------------------------------------
    # Hash functions
    # ------------------------------------------------------------------

    def _hash1(self, key) -> int:
        """Primary hash function using Python's built-in hash."""
        return hash(key) % self.capacity

    def _hash2(self, key) -> int:
        """
        Secondary hash function used by Double Hashing.
        Must return a value co-prime with capacity (ensure odd + non-zero).
        """
        h = hash(key)
        # Use a prime slightly smaller than capacity to avoid 0
        prime = self._largest_prime_below(self.capacity)
        return prime - (h % prime)

    @staticmethod
    def _largest_prime_below(n: int) -> int:
        """Return the largest prime strictly less than n."""
        def is_prime(num):
            if num < 2:
                return False
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    return False
            return True

        candidate = n - 1
        while candidate > 1:
            if is_prime(candidate):
                return candidate
            candidate -= 1
        return 1  # fallback (shouldn't reach here for n >= 3)

    # ------------------------------------------------------------------
    # Load factor & resizing
    # ------------------------------------------------------------------

    @property
    def load_factor(self) -> float:
        return self.size / self.capacity

    def _should_resize(self) -> bool:
        return self.load_factor >= self.load_factor_threshold

    def _resize(self):
        """Double capacity and rehash all existing key-value pairs."""
        old_table = self._table
        self.capacity *= 2
        self._table = [None] * self.capacity
        self.size = 0
        self._collision_count = 0

        for entry in old_table:
            if entry is not None:
                self._rehash_entry(entry)

    @abstractmethod
    def _rehash_entry(self, entry):
        """Re-insert a single entry into the resized table."""
        pass

    # ------------------------------------------------------------------
    # Core CRUD — subclasses must implement
    # ------------------------------------------------------------------

    @abstractmethod
    def insert(self, key, value) -> None:
        """Insert or update key-value pair."""
        pass

    @abstractmethod
    def search(self, key):
        """Return value for key, or None if not found."""
        pass

    @abstractmethod
    def delete(self, key) -> bool:
        """Delete key. Return True if deleted, False if not found."""
        pass

    # ------------------------------------------------------------------
    # Convenience operators
    # ------------------------------------------------------------------

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __getitem__(self, key):
        result = self.search(key)
        if result is None:
            raise KeyError(key)
        return result

    def __delitem__(self, key):
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(self, key):
        return self.search(key) is not None

    def __len__(self):
        return self.size

    def __repr__(self):
        name = self.__class__.__name__
        return (
            f"{name}(size={self.size}, capacity={self.capacity}, "
            f"load_factor={self.load_factor:.2f}, "
            f"collisions={self._collision_count})"
        )

    # ------------------------------------------------------------------
    # Stats helper (used in benchmarks)
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "size": self.size,
            "capacity": self.capacity,
            "load_factor": round(self.load_factor, 4),
            "collisions": self._collision_count,
        }