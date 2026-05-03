# logger.py
from dataclasses import dataclass
from hash_table import LinearProbingHashTable


# =====================================================
# 1. ProbeEvent dataclass
# =====================================================
@dataclass
class ProbeEvent:
    key: object
    h1: int
    probe_path: list
    steps: int
    is_collision: bool


# =====================================================
# 2. LoggedHashTable wrapper
# =====================================================
class LoggedHashTable:
    def __init__(self, table):
        """
        table = object từ core engine:
            ChainingHashTable(...)
            LinearProbingHashTable(...)
            DoubleHashingHashTable(...)
        """
        self.table = table
        self.events = []

    # -------------------------------------------------
    # INSERT + LOG
    # -------------------------------------------------
    def insert(self, key, value):
        path = self._compute_probe_path(key)

        event = ProbeEvent(
            key=key,
            h1=path[0],
            probe_path=path,
            steps=len(path),
            is_collision=len(path) > 1
        )

        self.events.append(event)

        self.table.insert(key, value)

    # -------------------------------------------------
    # Wrapper methods
    # -------------------------------------------------
    def search(self, key):
        return self.table.search(key)

    def delete(self, key):
        return self.table.delete(key)

    @property
    def load_factor(self):
        return self.table.load_factor

    # =================================================
    # 3. _compute_probe_path()
    # =================================================
    def _compute_probe_path(self, key):

        # -----------------------------
        # ChainingHashTable
        # -----------------------------
        if self.table.__class__.__name__ == "ChainingHashTable":
            return [self.table.hash1(key)]

        # -----------------------------
        # LinearProbingHashTable
        # -----------------------------
        elif self.table.__class__.__name__ == "LinearProbingHashTable":
            idx = self.table.hash1(key)
            path = []

            for i in range(self.table.size):
                slot = (idx + i) % self.table.size
                path.append(slot)

                if (
                    self.table.table[slot] is None or
                    self.table.table[slot] is self.table.DELETED
                ):
                    break

            return path

        # -----------------------------
        # DoubleHashingHashTable
        # -----------------------------
        elif self.table.__class__.__name__ == "DoubleHashingHashTable":
            h1 = self.table.hash1(key)
            h2 = self.table.hash2(key)

            path = []

            for i in range(self.table.size):
                slot = (h1 + i * h2) % self.table.size
                path.append(slot)

                if self.table.table[slot] is None:
                    break

            return path

        # fallback
        else:
            return [self.table.hash1(key)]

    # =================================================
    # 4. get_stats()
    # =================================================
    def get_stats(self):
        total = len(self.events)

        collisions = sum(1 for e in self.events if e.is_collision)

        avg_probe = (
            sum(e.steps for e in self.events) / total
            if total > 0 else 0
        )

        max_probe = (
            max(e.steps for e in self.events)
            if total > 0 else 0
        )

        return {
            "total_inserts": total,
            "collisions": collisions,
            "collision_rate": round(collisions / total, 2) if total else 0,
            "avg_probe_length": round(avg_probe, 2),
            "max_probe_length": max_probe,
            "load_factor": round(self.table.load_factor, 2),
            "items": self.table.n,
            "table_size": self.table.size
        }


# =====================================================
# 5. TEST
# =====================================================
if __name__ == "__main__":
    ht = LoggedHashTable(LinearProbingHashTable(size=11))

    keys = [10, 21, 32, 43, 54, 65, 76, 87, 98, 109]

    for k in keys:
        ht.insert(k, f"value_{k}")

    print("===== EVENTS =====")
    for e in ht.events:
        print(e)

    print("\n===== STATS =====")
    print(ht.get_stats())