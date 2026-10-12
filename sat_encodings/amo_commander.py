"""
Phương pháp mã hóa AMO Commander (Commander-Variable Encoding):
(Klieber & Kwon, 2007)

Ý tưởng:
- Chia tập n biến thành các nhóm không giao nhau G_1, G_2, ..., G_m có kích thước tối đa k (thường k=3).
- Với mỗi nhóm G_i, tạo một biến chỉ huy (commander variable) c_i đại diện cho việc
  có đúng 1 (hoặc ít nhất 1) biến trong nhóm G_i được bật.
- Ràng buộc:
  1. AMO nội bộ trong mỗi nhóm G_i: Pairwise cho các biến thuộc G_i.
  2. x -> c_i với mọi x thuộc G_i: (not x v c_i) (nếu biến trong nhóm bật, chỉ huy phải bật).
  3. c_i -> OR(G_i): (not c_i v x_1 v x_2 v ...) (nếu chỉ huy bật, phải có ít nhất 1 biến bật).
- Áp dụng đệ quy AMO lên tập các biến chỉ huy C = [c_1, c_2, ..., c_m] cho tới khi len(C) <= k.

Đặc tính:
- Số biến phụ: O(n / k)
- Số mệnh đề: O(n)
"""

from itertools import combinations
from typing import List, Tuple


def amo_commander(lits: List[int], top_id: int, k: int = 3) -> Tuple[List[List[int]], int]:
    """
    Tạo các mệnh đề At-Most-One (AMO) theo phương pháp Commander Encoding.

    Tham số:
        lits: Danh sách literal đầu vào.
        top_id: ID biến lớn nhất hiện tại (dùng để cấp phát biến commander).
        k: Kích thước tối đa của mỗi nhóm (mặc định k = 3).

    Trả về:
        (clauses, new_top_id): Danh sách mệnh đề CNF và ID biến lớn nhất sau khi cấp phát.
    """
    n = len(lits)
    if n <= 1:
        return [], top_id

    # Nếu kích thước nhỏ hơn hoặc bằng k, áp dụng pairwise trực tiếp
    if n <= k:
        clauses = [[-u, -v] for u, v in combinations(lits, 2)]
        return clauses, top_id

    current_top = top_id
    clauses: List[List[int]] = []
    commanders: List[int] = []

    # Chia các biến thành các nhóm con kích thước k
    groups = [lits[i:i + k] for i in range(0, n, k)]

    for group in groups:
        if len(group) == 1:
            # Nhóm 1 phần tử: chính biến đó đóng vai trò commander
            commanders.append(group[0])
        else:
            current_top += 1
            c = current_top
            commanders.append(c)

            # 1. AMO nội bộ trong nhóm
            for u, v in combinations(group, 2):
                clauses.append([-u, -v])

            # 2. x -> c (với mọi x trong nhóm)
            for u in group:
                clauses.append([-u, c])

            # 3. c -> OR(group)
            clauses.append([-c] + list(group))

    # Đệ quy ràng buộc AMO trên tập các commander variables
    rec_clauses, final_top = amo_commander(commanders, current_top, k=k)
    clauses.extend(rec_clauses)

    return clauses, final_top
