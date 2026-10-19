"""
Phương pháp mã hóa AMO Commander:
(Klieber & Kwon, 2007)

Chia n biến thành các nhóm con kích thước k (mặc định k=3).
Mỗi nhóm được đại diện bởi một biến commander.
Đệ quy ràng buộc AMO trên tập biến commander.

Đặc tính:
- Biến phụ: O(n / k)
- Số mệnh đề: O(n)
"""

from itertools import combinations
from typing import List, Tuple


def amo_commander(lits: List[int], top_id: int, k: int = 3) -> Tuple[List[List[int]], int]:
    n = len(lits)
    if n <= 1:
        return [], top_id

    if n <= k:
        clauses = [[-u, -v] for u, v in combinations(lits, 2)]
        return clauses, top_id

    current_top = top_id
    clauses: List[List[int]] = []
    commanders: List[int] = []

    groups = [lits[i:i + k] for i in range(0, n, k)]

    for group in groups:
        if len(group) == 1:
            commanders.append(group[0])
        else:
            current_top += 1
            c = current_top
            commanders.append(c)

            # 1. Pairwise AMO bên trong nhóm
            for u, v in combinations(group, 2):
                clauses.append([-u, -v])

            # 2. x -> c
            for u in group:
                clauses.append([-u, c])

            # 3. c -> OR(group)
            clauses.append([-c] + list(group))

    # Đệ quy AMO trên tập biến chỉ huy
    rec_clauses, final_top = amo_commander(commanders, current_top, k=k)
    clauses.extend(rec_clauses)

    return clauses, final_top
