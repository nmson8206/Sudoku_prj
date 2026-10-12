"""
Phương pháp mã hóa AMO Pairwise (Naive Encoding):
Với mỗi cặp biến (u, v), hai biến không thể đồng thời là True:
    not u v not v

Đặc tính:
- Biến phụ: 0
- Số mệnh đề: n * (n - 1) / 2 = O(n^2)
"""

from itertools import combinations
from typing import List, Tuple


def amo_pairwise(lits: List[int], top_id: int = 0) -> Tuple[List[List[int]], int]:
    """Tạo mệnh đề AMO theo phương pháp Pairwise."""
    clauses = [[-u, -v] for u, v in combinations(lits, 2)]
    return clauses, top_id
