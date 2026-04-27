class MyHashTable:
    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        """Cách dùng: ht['key'] = 'value'"""
        self._data[key] = value

    def __getitem__(self, key):
        """Cách dùng: print(ht['key'])"""
        return self._data.get(key)

    def __delitem__(self, key):
        """Cách dùng: del ht['key']"""
        if key in self._data:
            del self._data[key]

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)
    
    def display(self):
        return self._data
    
# ===============================
# TEST NHANH - chứng minh cải tiến
# ===============================
ht = MyHashTable()

print("1. Hash table ban đầu:")
print(ht.display())              # {}

# Insert dữ liệu
ht["alice"] = 100
ht["bob"] = 200
ht["carol"] = 300

print("\n2. Sau khi insert 3 phần tử:")
print(ht.display())              # {'alice':100,...}

# Search trực tiếp O(1)
print("\n3. Search key 'bob':")
print(ht["bob"])                # 200

# Update value không cần duyệt vòng lặp
ht["bob"] = 999

print("\n4. Sau khi update bob:")
print(ht.display())

# Membership test cực nhanh
print("\n5. Kiểm tra tồn tại key:")
print("alice" in ht)            # True
print("david" in ht)            # False

# Delete
del ht["alice"]

print("\n6. Sau khi xoá alice:")
print(ht.display())

# Size
print("\n7. Số phần tử hiện tại:")
print(len(ht))                  # 2