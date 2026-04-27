"""
Hash Table Implementations
==========================
Exports all four collision-resolution strategies for easy import.

Usage:
    from hash_table.implementation import ChainingHashTable
    from hash_table.implementation import LinearProbingHashTable
    from hash_table.implementation import QuadraticProbingHashTable
    from hash_table.implementation import DoubleHashingHashTable
"""

from .base_hash_table import BaseHashTable
from .chaining import ChainingHashTable
from .linear_probing import LinearProbingHashTable
from .quadratic_probing import QuadraticProbingHashTable
from .double_hashing import DoubleHashingHashTable

__all__ = [
    "BaseHashTable",
    "ChainingHashTable",
    "LinearProbingHashTable",
    "QuadraticProbingHashTable",
    "DoubleHashingHashTable",
]