"""
Phương pháp mã hóa ALO (At-Least-One):
Đảm bảo có ít nhất một literal trong danh sách mang giá trị True.

Mệnh đề CNF duy nhất:
    (x_1 v x_2 v ... v x_n)
"""

from typing import List


def at_least_one(lits: List[int]) -> List[List[int]]:
    """
    Tạo mệnh đề At-Least-One (ALO).

    Tham số:
        lits: Danh sách các literal (ví dụ: [x1, x2, ..., xn]).

    Trả về:
        Danh sách mệnh đề CNF (chứa 1 mệnh đề: [[x1, x2, ..., xn]]).
    """
    if not lits:
        return []
    return [list(lits)]
