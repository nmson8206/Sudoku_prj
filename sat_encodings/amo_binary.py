"""
Phương pháp mã hóa AMO Binary (Bitwise Encoding):
(Frisch et al., 2005)

Ý tưởng:
- Mỗi biến x_i được gán một vector bit nhị phân duy nhất biểu diễn chỉ số của nó:
    m = ceil(log2(n)) biến phụ b_1, b_2, ..., b_m.
- Nếu x_i = True thì các biến bit phụ b_j phải tương ứng với bit thứ j của x_i.
- Do mỗi x_i có vector bit duy nhất, không thể có hai biến x_i, x_k cùng True vì sẽ dẫn đến mâu thuẫn trên ít nhất một bit.

Đặc tính:
- Gọi thông qua thư viện: pysat.card.CardEnc với EncType.bitwise
- Số biến phụ: ceil(log2(n))
- Số mệnh đề: n * ceil(log2(n)) = O(n log n)
"""

from typing import List, Tuple
from pysat.card import CardEnc, EncType


def amo_binary(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    """
    Tạo các mệnh đề At-Most-One (AMO) theo phương pháp Binary qua PySAT.

    Tham số:
        lits: Danh sách literal đầu vào.
        top_id: ID biến lớn nhất hiện tại (dùng để cấp phát biến phụ bit).

    Trả về:
        (clauses, new_top_id): Danh sách mệnh đề CNF và ID biến lớn nhất sau khi cấp phát.
    """
    n = len(lits)
    if n <= 1:
        return [], top_id

    # Gọi hàm CardEnc.atmost của PySAT với chuẩn bitwise
    cnf = CardEnc.atmost(lits=lits, bound=1, encoding=EncType.bitwise, top_id=top_id)
    new_top_id = cnf.nv if cnf.nv > top_id else top_id
    return cnf.clauses, new_top_id
