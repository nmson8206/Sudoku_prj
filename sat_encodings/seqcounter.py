"""
Phương pháp mã hóa AMO Sequential Counter:
(Carsten Sinz, 2005)

Dùng chuỗi biến phụ s_1..s_{n-1} đại diện cho trạng thái tích lũy True từ tiền tố.
Sử dụng hàm của thư viện PySAT: pysat.card.CardEnc với EncType.seqcounter.

Đặc tính:
- Biến phụ: n - 1
- Số mệnh đề: 3n - 4 = O(n)
"""

from typing import List, Tuple
from pysat.card import CardEnc, EncType


def amo_seqcounter(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    n = len(lits)
    if n <= 1:
        return [], top_id

    cnf = CardEnc.atmost(lits=lits, bound=1, encoding=EncType.seqcounter, top_id=top_id)
    new_top_id = cnf.nv if cnf.nv > top_id else top_id
    return cnf.clauses, new_top_id
