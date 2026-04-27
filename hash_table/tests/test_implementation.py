"""
test_implementation.py
======================
Comprehensive tests for all four hash table strategies.
Run with:  pytest hash_table/tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest

from hash_table.implementation import (
    ChainingHashTable,
    LinearProbingHashTable,
    QuadraticProbingHashTable,
    DoubleHashingHashTable,
)

# All four classes to parametrize tests across
ALL_TABLES = [
    ChainingHashTable,
    LinearProbingHashTable,
    QuadraticProbingHashTable,
    DoubleHashingHashTable,
]


# ===========================================================================
# Helper
# ===========================================================================

def make_table(cls, capacity=16):
    return cls(capacity=capacity)


# ===========================================================================
# Parametrized basic tests (run for every implementation)
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
class TestBasicOperations:

    def test_insert_and_search(self, cls):
        ht = make_table(cls)
        ht.insert("name", "Alice")
        assert ht.search("name") == "Alice"

    def test_update_existing_key(self, cls):
        ht = make_table(cls)
        ht.insert("x", 1)
        ht.insert("x", 99)
        assert ht.search("x") == 99
        assert len(ht) == 1

    def test_search_missing_key(self, cls):
        ht = make_table(cls)
        assert ht.search("ghost") is None

    def test_delete_existing_key(self, cls):
        ht = make_table(cls)
        ht.insert("k", "v")
        result = ht.delete("k")
        assert result is True
        assert ht.search("k") is None
        assert len(ht) == 0

    def test_delete_missing_key(self, cls):
        ht = make_table(cls)
        assert ht.delete("missing") is False

    def test_len(self, cls):
        ht = make_table(cls)
        for i in range(10):
            ht.insert(i, i * 2)
        assert len(ht) == 10

    def test_contains(self, cls):
        ht = make_table(cls)
        ht.insert("hello", "world")
        assert "hello" in ht
        assert "bye" not in ht

    def test_dunder_setitem_getitem(self, cls):
        ht = make_table(cls)
        ht["key"] = "val"
        assert ht["key"] == "val"

    def test_dunder_getitem_missing_raises(self, cls):
        ht = make_table(cls)
        with pytest.raises(KeyError):
            _ = ht["nope"]

    def test_dunder_delitem(self, cls):
        ht = make_table(cls)
        ht["key"] = "val"
        del ht["key"]
        assert "key" not in ht

    def test_dunder_delitem_missing_raises(self, cls):
        ht = make_table(cls)
        with pytest.raises(KeyError):
            del ht["ghost"]


# ===========================================================================
# Resize / rehash tests
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
class TestResizing:

    def test_resize_preserves_data(self, cls):
        ht = make_table(cls, capacity=4)
        data = {str(i): i for i in range(30)}
        for k, v in data.items():
            ht.insert(k, v)
        for k, v in data.items():
            assert ht.search(k) == v, f"Key {k!r} lost after resize"

    def test_capacity_grows(self, cls):
        ht = make_table(cls, capacity=4)
        for i in range(20):
            ht.insert(i, i)
        assert ht.capacity > 4

    def test_size_correct_after_resize(self, cls):
        ht = make_table(cls, capacity=4)
        for i in range(20):
            ht.insert(i, i)
        assert len(ht) == 20


# ===========================================================================
# Load factor & stats
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
class TestLoadFactor:

    def test_load_factor_zero_when_empty(self, cls):
        ht = make_table(cls)
        assert ht.load_factor == 0.0

    def test_load_factor_increases_on_insert(self, cls):
        ht = make_table(cls, capacity=16)
        for i in range(5):
            ht.insert(i, i)
        assert ht.load_factor == pytest.approx(5 / ht.capacity, abs=1e-6)

    def test_stats_returns_dict(self, cls):
        ht = make_table(cls)
        s = ht.stats()
        assert isinstance(s, dict)
        assert "load_factor" in s
        assert "collisions" in s


# ===========================================================================
# Stress test: large number of keys
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
def test_stress_insert_search_delete(cls):
    ht = make_table(cls, capacity=16)
    n = 500
    for i in range(n):
        ht.insert(f"key_{i}", i)

    # All keys searchable
    for i in range(n):
        assert ht.search(f"key_{i}") == i

    # Delete half
    for i in range(0, n, 2):
        assert ht.delete(f"key_{i}") is True

    # Deleted keys gone, odd keys still present
    for i in range(n):
        if i % 2 == 0:
            assert ht.search(f"key_{i}") is None
        else:
            assert ht.search(f"key_{i}") == i


# ===========================================================================
# Integer and mixed-type keys
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
def test_integer_keys(cls):
    ht = make_table(cls)
    for i in range(50):
        ht[i] = i ** 2
    for i in range(50):
        assert ht[i] == i ** 2


@pytest.mark.parametrize("cls", ALL_TABLES)
def test_tuple_keys(cls):
    ht = make_table(cls)
    ht[(1, 2)] = "point"
    assert ht.search((1, 2)) == "point"
    assert ht.search((2, 1)) is None


# ===========================================================================
# Chaining-specific: visualize & iteration
# ===========================================================================

def test_chaining_visualize():
    ht = ChainingHashTable(capacity=8)
    ht.insert("a", 1)
    ht.insert("b", 2)
    out = ht.visualize()
    assert "ChainingHashTable" in out


def test_chaining_keys_values_items():
    ht = ChainingHashTable()
    ht["x"] = 10
    ht["y"] = 20
    assert set(ht.keys()) == {"x", "y"}
    assert set(ht.values()) == {10, 20}
    assert set(ht.items()) == {("x", 10), ("y", 20)}


# ===========================================================================
# Open addressing: tombstone / delete-then-search
# ===========================================================================

@pytest.mark.parametrize("cls", [
    LinearProbingHashTable,
    QuadraticProbingHashTable,
    DoubleHashingHashTable,
])
def test_delete_then_search_still_works(cls):
    """
    After deleting a key, searching for a key that was inserted AFTER it
    must still succeed (tombstone must not break the probe chain).
    """
    ht = cls(capacity=8)
    # Force two keys to same initial bucket
    keys = [k for k in range(100) if hash(k) % 8 == 0][:3]
    for k in keys:
        ht.insert(k, k)

    # Delete the first one (creates tombstone)
    ht.delete(keys[0])

    # The second and third keys must still be found
    assert ht.search(keys[1]) == keys[1]
    assert ht.search(keys[2]) == keys[2]


# ===========================================================================
# Repr smoke test
# ===========================================================================

@pytest.mark.parametrize("cls", ALL_TABLES)
def test_repr(cls):
    ht = make_table(cls)
    r = repr(ht)
    assert cls.__name__ in r