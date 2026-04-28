from .base_hash_table import BaseHashTable

class LinearProbingHashTable(BaseHashTable):
    """
    Built-in Version: Uses Python's built-in dict.
    - No need for _probe(): dict handles collisions internally.
    - No need for _DELETED: dict manages key deletion automatically.
    - No need for _resize(): dict resizes dynamically when needed.
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
        return f"LinearProbingHashTable (Managed by Python dict): {self._table}"