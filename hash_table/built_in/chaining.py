from .base_hash_table import BaseHashTable 

class ChainingHashTable(BaseHashTable): 
    def __init__(self, capacity: int = 16):
        super().__init__()

    # ------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------

    def insert(self, key, value) -> None:
        self._table[key] = value

    def search(self, key):
        return self._table.get(key)

    def delete(self, key) -> bool:
        return self._table.pop(key, None) is not None

    # ------------------------------------------------------------
    # Iterators & Stats
    # ------------------------------------------------------------

    def keys(self):
        return self._table.keys()

    def values(self):
        return self._table.values()

    def items(self):
        return self._table.items()

    def __len__(self):
        return len(self._table)

    def __iter__(self):
        return iter(self._table)

    def visualize(self) -> str:
        """ASCII visualization."""
        lines = [f"ChainingHashTable (Managed by Python dict):"]
        for k, v in self._table.items():
            lines.append(f"  [{k!r}: {v!r}]")
        return "\n".join(lines)