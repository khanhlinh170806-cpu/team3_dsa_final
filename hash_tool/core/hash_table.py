class HashTableBase:
    def __init__(self, size=11):
        self.size = size
        self.table = [None] * size
        self.n = 0

    def hash1(self, key):
        try:
            return int(key) % self.size        # ✅ fix: int key dùng giá trị số
        except (ValueError, TypeError):
            return hash(key) % self.size        # string key dùng hash()

    @property
    def load_factor(self):
        return self.n / self.size

    def insert(self, key, value): raise NotImplementedError
    def search(self, key):        raise NotImplementedError
    def delete(self, key):        raise NotImplementedError


class ChainingHashTable(HashTableBase):
    def __init__(self, size=11):
        super().__init__(size)
        self.table = [[] for _ in range(size)]

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
    DELETED = object()

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


class QuadraticProbingHashTable(HashTableBase):
    DELETED = object()

    def insert(self, key, value):
        h1 = self.hash1(key)
        for i in range(self.size):
            slot = (h1 + i * i) % self.size
            if self.table[slot] is None or self.table[slot] is self.DELETED:
                self.table[slot] = (key, value)
                self.n += 1
                return
            if self.table[slot][0] == key:
                self.table[slot] = (key, value)
                return
        raise Exception("Table is full")

    def search(self, key):
        h1 = self.hash1(key)
        for i in range(self.size):
            slot = (h1 + i * i) % self.size
            if self.table[slot] is None:
                return None
            if self.table[slot] is not self.DELETED and self.table[slot][0] == key:
                return self.table[slot][1]
        return None

    def delete(self, key):
        h1 = self.hash1(key)
        for i in range(self.size):
            slot = (h1 + i * i) % self.size
            if self.table[slot] is None:
                return
            if self.table[slot] is not self.DELETED and self.table[slot][0] == key:
                self.table[slot] = self.DELETED
                self.n -= 1
                return


class DoubleHashingHashTable(HashTableBase):
    def hash2(self, key):
        try:
            return 7 - (int(key) % 7)          # ✅ fix: int key dùng giá trị số
        except (ValueError, TypeError):
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
    ht = LinearProbingHashTable(size=11)
    print(ht.hash1("29"))   # phải ra 7
    print(ht.hash1(29))     # phải ra 7
    print(ht.hash1("abc"))  # ra số tùy hash, không lỗi

    ht.insert("alice", 1)
    ht.insert("bob", 2)
    ht.insert("carol", 3)
    print(ht.table)
    print(ht.load_factor)
    print(ht.search("bob"))