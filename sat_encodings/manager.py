"""
Bộ điều phối chung (Cardinality Manager) cho ALO, AMO và Exactly-One (EO).
"""

from typing import List, Tuple
from .alo import at_least_one
from .pairwise import amo_pairwise
from .binary import amo_binary
from .commander import amo_commander
from .product import amo_product
from .seqcounter import amo_seqcounter


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
    Điều phối sinh các mệnh đề At-Most-One (AMO).
    
    Phương pháp hỗ trợ:
    - 'pairwise' (mặc định)
    - 'binary' (hoặc 'bitwise')
    - 'commander'
    - 'product' (hoặc '2-product')
    - 'seqcounter' (hoặc 'sequential_counter')
    """
    key = method.lower().strip()
    if key not in AVAILABLE_METHODS:
        valid_keys = sorted(list(set(["pairwise", "binary", "commander", "product", "seqcounter"])))
        raise ValueError(f"Phương pháp không hợp lệ: '{method}'. Vui lòng chọn một trong: {valid_keys}")

    return AVAILABLE_METHODS[key](lits, top_id=top_id)


def exactly_one(lits: List[int], method: str = "pairwise", top_id: int = 0) -> Tuple[List[List[int]], int]:
    """
    Ràng buộc Exactly-One (EO) = ALO + AMO.
    """
    alo_cls = at_least_one(lits)
    amo_cls, new_top_id = at_most_one(lits, method=method, top_id=top_id)
    return alo_cls + amo_cls, new_top_id
