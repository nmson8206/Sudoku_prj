"""
Package sat_encodings:
Cung cấp các phương pháp mã hóa SAT cho ALO (At-Least-One) và AMO (At-Most-One).
"""

from .alo import at_least_one
from .amo_pairwise import amo_pairwise
from .amo_binary import amo_binary
from .amo_commander import amo_commander
from .amo_product import amo_product
from .amo_seqcounter import amo_seqcounter
from .cardinality_manager import at_most_one, exactly_one, AVAILABLE_METHODS

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
