"""
Phương pháp mã hóa ALO (At-Least-One):
Đảm bảo ít nhất một literal trong danh sách mang giá trị True:
    (x_1 v x_2 v ... v x_n)
"""

from typing import List


def at_least_one(lits: List[int]) -> List[List[int]]:
    """Tạo mệnh đề At-Least-One (ALO)."""
    if not lits:
        return []
    return [list(lits)]
