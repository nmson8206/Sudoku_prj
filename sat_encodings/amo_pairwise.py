"""
Phương pháp mã hóa AMO Pairwise (Naive Encoding):
Với mỗi cặp biến (u, v), hai biến không thể đồng thời là True:
    not u v not v

Đặc tính:
- Số biến phụ: 0 biến phụ.
- Số mệnh đề: n * (n - 1) / 2 = O(n^2).
- Thích hợp khi n nhỏ (như n=3, 4). Khi n lớn, số mệnh đề tăng nhanh bậc hai.
"""

from itertools import combinations
from typing import List, Tuple


def amo_pairwise(lits: List[int], top_id: int = 0) -> Tuple[List[List[int]], int]:
    """
    Tạo các mệnh đề At-Most-One (AMO) theo phương pháp Pairwise.

    Tham số:
        lits: Danh sách literal đầu vào.
        top_id: ID biến lớn nhất hiện tại (không dùng biến phụ, giữ nguyên).

    Trả về:
        (clauses, top_id): Danh sách mệnh đề CNF và ID biến không đổi.
    """
    clauses = [[-u, -v] for u, v in combinations(lits, 2)]
    return clauses, top_id
