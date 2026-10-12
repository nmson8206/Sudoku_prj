"""
Phương pháp mã hóa AMO Binary (Bitwise Encoding):
(Frisch et al., 2005)

Sử dụng thư viện PySAT: pysat.card.CardEnc với EncType.bitwise.

Đặc tính:
- Biến phụ: ceil(log2(n))
- Số mệnh đề: n * ceil(log2(n)) = O(n log n)
"""

from typing import List, Tuple
from pysat.card import CardEnc, EncType


def amo_binary(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    """Tạo mệnh đề AMO theo phương pháp Binary qua PySAT."""
    n = len(lits)
    if n <= 1:
        return [], top_id

    cnf = CardEnc.atmost(lits=lits, bound=1, encoding=EncType.bitwise, top_id=top_id)
    new_top_id = cnf.nv if cnf.nv > top_id else top_id
    return cnf.clauses, new_top_id
