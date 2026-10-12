"""
Phương pháp mã hóa AMO Sequential Counter:
(Carsten Sinz, 2005)

Ý tưởng:
- Tạo một chuỗi biến đếm phụ s_1, s_2, ..., s_{n-1}.
- Biến s_i đại diện cho việc: "đã có ít nhất 1 biến mang giá trị True trong tiền tố x_1, ..., x_i".
- Khi x_i = True, nó kích hoạt s_i = True.
- Trạng thái True được lan truyền từ s_{i-1} sang s_i.
- Ràng buộc ngăn ngừa: nếu s_{i-1} = True thì x_i KHÔNG ĐƯỢC PHÉP True:
    (not x_i v not s_{i-1})

Đặc tính:
- Gọi thông qua thư viện: pysat.card.CardEnc với EncType.seqcounter
- Số biến phụ: n - 1
- Số mệnh đề: 3n - 4 = O(n)
"""

from typing import List, Tuple
from pysat.card import CardEnc, EncType


def amo_seqcounter(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    """
    Tạo các mệnh đề At-Most-One (AMO) theo phương pháp Sequential Counter qua PySAT.

    Tham số:
        lits: Danh sách literal đầu vào.
        top_id: ID biến lớn nhất hiện tại (dùng để cấp phát biến đếm s_i).

    Trả về:
        (clauses, new_top_id): Danh sách mệnh đề CNF và ID biến lớn nhất sau khi cấp phát.
    """
    n = len(lits)
    if n <= 1:
        return [], top_id

    # Gọi hàm CardEnc.atmost của PySAT với chuẩn seqcounter (Sinz)
    cnf = CardEnc.atmost(lits=lits, bound=1, encoding=EncType.seqcounter, top_id=top_id)
    new_top_id = cnf.nv if cnf.nv > top_id else top_id
    return cnf.clauses, new_top_id
