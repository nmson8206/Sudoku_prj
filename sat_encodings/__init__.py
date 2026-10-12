"""
Package encodings: Các kỹ thuật mã hóa SAT cho ALO, AMO và Exactly-One (EO).
"""

from .alo import at_least_one
from .pairwise import amo_pairwise
from .binary import amo_binary
from .commander import amo_commander
from .product import amo_product
from .seqcounter import amo_seqcounter
from .manager import at_most_one, exactly_one, AVAILABLE_METHODS

__all__ = [
    "at_least_one",
    "amo_pairwise",
    "amo_binary",
    "amo_commander",
    "amo_product",
    "amo_seqcounter",
    "at_most_one",
    "exactly_one",
    "AVAILABLE_METHODS",
]
