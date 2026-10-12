"""
Phương pháp mã hóa AMO Product (2-Product Encoding):
(Jingchao Chen, 2010)

Ý tưởng:
- Bố trí n biến x_1, ..., x_n vào một lưới 2 chiều kích thước p x q sao cho p * q >= n.
  Chọn p = ceil(sqrt(n)), q = ceil(n / p).
- Tạo p biến hàng r_1, ..., r_p và q biến cột c_1, ..., c_q.
- Mỗi biến x_k ở tọa độ (hàng i, cột j):
  - x_k -> r_i   <=>   (not x_k v r_i)
  - x_k -> c_j   <=>   (not x_k v c_j)
- Ràng buộc At-Most-One trên các biến hàng và biến cột:
  - AMO(r_1, ..., r_p)
  - AMO(c_1, ..., c_q)

Chứng minh tính đúng đắn:
- Nếu có 2 biến x_a, x_b cùng True:
  + Nếu cùng hàng i: chúng khác cột -> 2 biến cột c_ja, c_jb cùng True -> vi phạm AMO(c).
  + Nếu cùng cột j: chúng khác hàng -> 2 biến hàng r_ia, r_ib cùng True -> vi phạm AMO(r).
  + Nếu khác cả hàng và cột: vi phạm cả AMO(r) và AMO(c).
- Do đó không thể có 2 biến ban đầu nào cùng True.

Đặc tính:
- Số biến phụ: p + q = 2 * ceil(sqrt(n)) = O(sqrt(n)).
- Số mệnh đề: 2n + O(p^2 + q^2) = O(n).
"""

import math
from itertools import combinations
from typing import List, Tuple


def amo_product(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    """
    Tạo các mệnh đề At-Most-One (AMO) theo phương pháp 2-Product Encoding.

    Tham số:
        lits: Danh sách literal đầu vào.
        top_id: ID biến lớn nhất hiện tại (dùng để cấp phát biến hàng và cột).

    Trả về:
        (clauses, new_top_id): Danh sách mệnh đề CNF và ID biến lớn nhất sau khi cấp phát.
    """
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

    # Ánh xạ x_k vào (r_i, c_j)
    for idx, x in enumerate(lits):
        i = idx // q
        j = idx % q
        clauses.append([-x, rows[i]])
        clauses.append([-x, cols[j]])

    # AMO trên tập biến hàng (dùng pairwise vì p nhỏ ~ sqrt(n))
    for u, v in combinations(rows, 2):
        clauses.append([-u, -v])

    # AMO trên tập biến cột (dùng pairwise vì q nhỏ ~ sqrt(n))
    for u, v in combinations(cols, 2):
        clauses.append([-u, -v])

    return clauses, current_top
