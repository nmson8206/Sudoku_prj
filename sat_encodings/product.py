"""
Phương pháp mã hóa AMO Product (2-Product Encoding):
(Jingchao Chen, 2010)

Bố trí n biến vào ma trận 2 chiều kích thước p x q (p*q >= n).
Tạo biến hàng r_1..r_p và biến cột c_1..c_q.
Ánh xạ: x_ij -> r_i và x_ij -> c_j.
Áp dụng AMO trên hàng và cột.

Đặc tính:
- Biến phụ: 2 * ceil(sqrt(n)) = O(sqrt(n))
- Số mệnh đề: O(n)
"""

import math
from itertools import combinations
from typing import List, Tuple


def amo_product(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    n = len(lits)
    if n <= 1:
        return [], top_id

    if n <= 3:
        clauses = [[-u, -v] for u, v in combinations(lits, 2)]
        return clauses, top_id

    p = math.ceil(math.sqrt(n))
    q = math.ceil(n / p)

    current_top = top_id
    rows = []
    for _ in range(p):
        current_top += 1
        rows.append(current_top)

    cols = []
    for _ in range(q):
        current_top += 1
        cols.append(current_top)

    clauses: List[List[int]] = []

    for idx, x in enumerate(lits):
        i = idx // q
        j = idx % q
        clauses.append([-x, rows[i]])
        clauses.append([-x, cols[j]])

    for u, v in combinations(rows, 2):
        clauses.append([-u, -v])

    for u, v in combinations(cols, 2):
        clauses.append([-u, -v])

    return clauses, current_top
