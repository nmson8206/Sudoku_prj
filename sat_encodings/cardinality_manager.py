"""
Bộ điều phối chung (Cardinality Manager) cho các phương pháp ALO, AMO và EO.
"""

from typing import List, Tuple
from .alo import at_least_one
from .amo_pairwise import amo_pairwise
from .amo_binary import amo_binary
from .amo_commander import amo_commander
from .amo_product import amo_product
from .amo_seqcounter import amo_seqcounter


AVAILABLE_METHODS = {
    "pairwise": amo_pairwise,
    "naive": amo_pairwise,
    "binary": amo_binary,
    "bitwise": amo_binary,
    "commander": amo_commander,
    "product": amo_product,
    "2-product": amo_product,
    "seqcounter": amo_seqcounter,
    "sequential_counter": amo_seqcounter,
}


def at_most_one(lits: List[int], method: str = "pairwise", top_id: int = 0) -> Tuple[List[List[int]], int]:
    """
    Điều phối sinh các mệnh đề At-Most-One (AMO) theo phương pháp được chỉ định.

    Tham số:
        lits: Danh sách literal đầu vào.
        method: Tên phương pháp ('pairwise', 'binary', 'commander', 'product', 'seqcounter').
        top_id: ID biến lớn nhất hiện tại.

    Trả về:
        (clauses, new_top_id): Danh sách mệnh đề CNF và ID biến mới nhất.
    """
    key = method.lower().strip()
    if key not in AVAILABLE_METHODS:
        valid_names = sorted(list(set(["pairwise", "binary", "commander", "product", "seqcounter"])))
        raise ValueError(
            f"Phương pháp không hợp lệ: '{method}'. "
            f"Vui lòng chọn một trong: {valid_names}"
        )

    fn = AVAILABLE_METHODS[key]
    return fn(lits, top_id=top_id)


def exactly_one(lits: List[int], method: str = "pairwise", top_id: int = 0) -> Tuple[List[List[int]], int]:
    """
    Ràng buộc Exactly-One (EO): Có đúng 1 literal mang giá trị True.
    EO = ALO (At-Least-One) + AMO (At-Most-One).

    Tham số:
        lits: Danh sách literal đầu vào.
        method: Tên phương pháp AMO ('pairwise', 'binary', 'commander', 'product', 'seqcounter').
        top_id: ID biến lớn nhất hiện tại.

    Trả về:
        (clauses, new_top_id): Danh sách mệnh đề CNF và ID biến mới nhất.
    """
    alo_clauses = at_least_one(lits)
    amo_clauses, new_top_id = at_most_one(lits, method=method, top_id=top_id)
    return alo_clauses + amo_clauses, new_top_id
