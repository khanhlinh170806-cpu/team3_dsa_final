class HashTableBase:
    def __init__(self, size=11):
        self.size = size
        self.table = [None] * size
        self.n = 0  # số phần tử hiện tại

    def hash1(self, key):
        return hash(key) % self.size

    @property
    def load_factor(self):
        return self.n / self.size

    def insert(self, key, value): raise NotImplementedError
    def search(self, key):        raise NotImplementedError
    def delete(self, key):        raise NotImplementedError


class ChainingHashTable(HashTableBase):
    def __init__(self, size=11):
        super().__init__(size)
        self.table = [[] for _ in range(size)]  # mỗi slot là 1 list

    def insert(self, key, value):
        idx = self.hash1(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, value)
                return
        self.table[idx].append((key, value))
        self.n += 1

    def search(self, key):
        idx = self.hash1(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

    def delete(self, key):
        idx = self.hash1(key)
        self.table[idx] = [(k, v) for k, v in self.table[idx] if k != key]
        self.n -= 1


class LinearProbingHashTable(HashTableBase):
    DELETED = object()  # sentinel cho deleted slot

    def insert(self, key, value):
        idx = self.hash1(key)
        for i in range(self.size):
            slot = (idx + i) % self.size
            if self.table[slot] is None or self.table[slot] is self.DELETED:
                self.table[slot] = (key, value)
                self.n += 1
                return
            if self.table[slot][0] == key:
                self.table[slot] = (key, value)
                return
        raise Exception("Table is full")

    def search(self, key):
        idx = self.hash1(key)
        for i in range(self.size):
            slot = (idx + i) % self.size
            if self.table[slot] is None:
                return None
            if self.table[slot] is not self.DELETED and self.table[slot][0] == key:
                return self.table[slot][1]
        return None

    def delete(self, key):
        idx = self.hash1(key)
        for i in range(self.size):
            slot = (idx + i) % self.size
            if self.table[slot] is None:
                return
            if self.table[slot] is not self.DELETED and self.table[slot][0] == key:
                self.table[slot] = self.DELETED
                self.n -= 1
                return


class DoubleHashingHashTable(HashTableBase):
    def hash2(self, key):
        # hash2 phải trả về số lẻ để đảm bảo probe hết mọi slot
        return 7 - (hash(key) % 7)

    def insert(self, key, value):
        h1 = self.hash1(key)
        h2 = self.hash2(key)
        for i in range(self.size):
            slot = (h1 + i * h2) % self.size
            if self.table[slot] is None:
                self.table[slot] = (key, value)
                self.n += 1
                return
            if self.table[slot][0] == key:
                self.table[slot] = (key, value)
                return

    def search(self, key):
        h1 = self.hash1(key)
        h2 = self.hash2(key)
        for i in range(self.size):
            slot = (h1 + i * h2) % self.size
            if self.table[slot] is None:
                return None
            if self.table[slot][0] == key:
                return self.table[slot][1]
        return None

# test nhanh
if __name__ == "__main__":
    ht = LinearProbingHashTable(size=7)
    ht.insert("alice", 1)
    ht.insert("bob", 2)
    ht.insert("carol", 3)
    print(ht.table)           # thấy được slot nào bị chiếm
    print(ht.load_factor)     # ~0.43
    print(ht.search("bob"))   # 2