"""
Facade module trỏ tới package sat_encodings.
Giữ tính tương thích ngược cho toàn bộ codebase.
"""

from sat_encodings import (
    at_least_one,
    amo_pairwise,
    amo_binary,
    amo_commander,
    amo_product,
    amo_seqcounter,
    at_most_one,
    exactly_one,
    AVAILABLE_METHODS,
)

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
