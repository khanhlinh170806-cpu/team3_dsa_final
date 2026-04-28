from .base_hash_table import BaseHashTable

class QuadraticProbingHashTable(BaseHashTable):
    """
    Built-in Version: Utilizes Python's built-in dictionary hashing mechanism.

    In Python, dict is highly optimized for average-case O(1) lookup performance.
    There is no need to manually implement quadratic probing (i^2), since dict
    uses a more advanced modern variant of open addressing that helps mitigate
    both primary clustering and secondary clustering.
    """

    def insert(self, key, value):
        self._table[key] = value

    def search(self, key):
        return self._table.get(key)

    def delete(self, key) -> bool:
        return self._table.pop(key, None) is not None

    # ------------------------------------------------------------
    # Iterators
    # ------------------------------------------------------------

    def keys(self):
        return self._table.keys()

    def values(self):
        return self._table.values()

    def items(self):
        return self._table.items()

    def __iter__(self):
        return iter(self._table)

    def visualize(self) -> str:
        return f"QuadraticProbingHashTable (Managed by Python dict): {self._table}"