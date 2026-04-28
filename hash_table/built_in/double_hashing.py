from .base_hash_table import BaseHashTable

class DoubleHashingHashTable(BaseHashTable):

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
        return f"DoubleHashingHashTable (Managed by dict): {self._table}"