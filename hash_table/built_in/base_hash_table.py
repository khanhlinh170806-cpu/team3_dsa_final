"""
Built-in Python Hash Table Version
Refactor from manual implementation -> uses Python dict internally
"""

from abc import ABC, abstractmethod


class BaseHashTable(ABC):
    """
    Base class using Python built-in dict.
    Faster, cleaner, no manual collision handling needed.
    """

    def __init__(self):
        self._table = {}
        self._collision_count = 0   # kept only for compatibility

    # ------------------------------------------------------------
    # Basic stats
    # ------------------------------------------------------------

    @property
    def size(self):
        return len(self._table)

    @property
    def capacity(self):
        return "Managed by Python"

    @property
    def load_factor(self):
        return "Auto managed"

    # ------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------

    def insert(self, key, value):
        self._table[key] = value

    def search(self, key):
        return self._table.get(key, None)

    def delete(self, key):
        return self._table.pop(key, None) is not None

    # ------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __getitem__(self, key):
        if key not in self._table:
            raise KeyError(key)
        return self._table[key]

    def __delitem__(self, key):
        if key not in self._table:
            raise KeyError(key)
        del self._table[key]

    def __contains__(self, key):
        return key in self._table

    def __len__(self):
        return len(self._table)

    def __repr__(self):
        return f"{self.__class__.__name__}(size={self.size})"

    # ------------------------------------------------------------
    # Benchmark stats
    # ------------------------------------------------------------

    def stats(self):
        return {
            "class": self.__class__.__name__,
            "size": self.size,
            "capacity": "dynamic",
            "load_factor": "managed internally",
            "collisions": "hidden by Python dict"
        }


# ------------------------------------------------------------
# Derived classes (for naming comparison only)
# ------------------------------------------------------------

class ChainingHashTable(BaseHashTable):
    pass


class LinearProbingHashTable(BaseHashTable):
    pass


class DoubleHashingHashTable(BaseHashTable):
    pass