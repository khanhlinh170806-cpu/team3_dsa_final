import pytest
from built_in.chaining import ChainingHashTable
from built_in.linear_probing import LinearProbingHashTable
from built_in.double_hashing import DoubleHashingHashTable
from built_in.quadratic_probing import QuadraticProbingHashTable

# Danh sách các class để chạy test hàng loạt
ALL_TABLES = [
    ChainingHashTable,
    LinearProbingHashTable,
    DoubleHashingHashTable,
    QuadraticProbingHashTable,
]

# ===========================================================================
# Basic Operations (Dùng chung cho cả 4 class)
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
class TestBasicOperations:

    def test_insert_and_search(self, cls):
        ht = cls()
        ht.insert("name", "Alice")
        assert ht.search("name") == "Alice"

    def test_update_existing_key(self, cls):
        ht = cls()
        ht.insert("x", 1)
        ht.insert("x", 99)
        assert ht.search("x") == 99
        assert len(ht) == 1

    def test_search_missing_key(self, cls):
        ht = cls()
        assert ht.search("ghost") is None

    def test_delete_existing_key(self, cls):
        ht = cls()
        ht.insert("k", "v")
        result = ht.delete("k")
        assert result is True
        assert ht.search("k") is None
        assert len(ht) == 0

    def test_dunder_getitem_setitem(self, cls):
        ht = cls()
        ht["key"] = "val"
        assert ht["key"] == "val"

    def test_contains(self, cls):
        ht = cls()
        ht["hello"] = "world"
        assert "hello" in ht

# ===========================================================================
# Test Stress & Dữ liệu lớn
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
def test_stress_insert_search_delete(cls):
    ht = cls()
    n = 500
    for i in range(n):
        ht[f"key_{i}"] = i

    for i in range(n):
        assert ht[f"key_{i}"] == i

    for i in range(0, n, 2):
        assert ht.delete(f"key_{i}") is True

    for i in range(n):
        if i % 2 == 0:
            assert ht.search(f"key_{i}") is None
        else:
            assert ht[f"key_{i}"] == i

# ===========================================================================
# Test Tính năng phụ (Visualization & Stats)
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
def test_stats_and_visualize(cls):
    ht = cls()
    ht["a"] = 1
    # Kiểm tra stats trả về dict và có các key cần thiết
    stats = ht.stats()
    assert isinstance(stats, dict)
    assert "size" in stats
    
    # Kiểm tra visualize trả về string
    vis = ht.visualize()
    assert isinstance(vis, str)
    assert "a" in vis

# ===========================================================================
# Test Key Types
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
def test_various_keys(cls):
    ht = cls()
    keys = [1, "string", (1, 2), 3.14]
    for k in keys:
        ht[k] = "value"
        assert ht[k] == "value"