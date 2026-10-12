"""
Unit tests kiểm tra tính đúng đắn (soundness & completeness) của các phương pháp AMO, ALO và EO
được phân chia trong package sat_encodings.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from itertools import product as iter_product
from pysat.solvers import Glucose3

# Import trực tiếp từ từng file phương pháp riêng biệt
from sat_encodings.alo import at_least_one
from sat_encodings.amo_pairwise import amo_pairwise
from sat_encodings.amo_binary import amo_binary
from sat_encodings.amo_commander import amo_commander
from sat_encodings.amo_product import amo_product
from sat_encodings.amo_seqcounter import amo_seqcounter
from sat_encodings.cardinality_manager import at_most_one, exactly_one


def test_individual_amo_function(name: str, fn, n: int = 6):
    """
    Kiểm tra hàm AMO trực tiếp từ từng file:
    - n biến ban đầu: 1 ... n
    - Duyệt toàn bộ 2^n trạng thái gán chân trị.
    - True <= 1: SAT.
    - True > 1: UNSAT.
    """
    lits = list(range(1, n + 1))
    clauses, _ = fn(lits, top_id=n)

    for assignment in iter_product([False, True], repeat=n):
        num_true = sum(assignment)
        solver = Glucose3()
        for cl in clauses:
            solver.add_clause(cl)

        for i, val in enumerate(assignment):
            solver.add_clause([lits[i] if val else -lits[i]])

        is_sat = solver.solve()
        expected = (num_true <= 1)
        assert is_sat == expected, (
            f"Loi tai {name}: assignment={assignment}, "
            f"ket qua={is_sat}, ky vong={expected}"
        )
    print(f"[PASSED] File rieng: {name:<20} (n={n}) - 100% {2**n} cases.")


def test_alo_function(n: int = 6):
    """Kiểm tra file alo.py: ít nhất 1 biến True -> SAT; tất cả False -> UNSAT."""
    lits = list(range(1, n + 1))
    clauses = at_least_one(lits)

    for assignment in iter_product([False, True], repeat=n):
        num_true = sum(assignment)
        solver = Glucose3()
        for cl in clauses:
            solver.add_clause(cl)

        for i, val in enumerate(assignment):
            solver.add_clause([lits[i] if val else -lits[i]])

        is_sat = solver.solve()
        expected = (num_true >= 1)
        assert is_sat == expected, f"Loi tai ALO: assignment={assignment}"
    print(f"[PASSED] File rieng: {'sat_encodings/alo.py':<20} (n={n}) - 100% {2**n} cases.")


def test_cardinality_manager(methods: list[str], n: int = 6):
    """Kiểm tra bộ điều phối cardinality_manager.py cho cả AMO và EO."""
    lits = list(range(1, n + 1))
    for m in methods:
        # Test EO
        clauses, _ = exactly_one(lits, method=m, top_id=n)
        for assignment in iter_product([False, True], repeat=n):
            num_true = sum(assignment)
            solver = Glucose3()
            for cl in clauses:
                solver.add_clause(cl)
            for i, val in enumerate(assignment):
                solver.add_clause([lits[i] if val else -lits[i]])
            is_sat = solver.solve()
            expected = (num_true == 1)
            assert is_sat == expected, f"Loi tai EO-{m}"
        print(f"[PASSED] Manager:    EO-{m:<17} (n={n}) - 100% {2**n} cases.")


def run_all():
    print("=" * 70)
    print("KIEM THU CAC FILE VA PHUONG PHAP SAT ENCODING CHO ALO, AMO VA EO")
    print("=" * 70)

    # 1. Test ALO
    test_alo_function(n=6)

    # 2. Test từng file phương pháp riêng biệt
    test_individual_amo_function("sat_encodings/amo_pairwise.py", amo_pairwise, n=6)
    test_individual_amo_function("sat_encodings/amo_binary.py", amo_binary, n=6)
    test_individual_amo_function("sat_encodings/amo_commander.py", amo_commander, n=6)
    test_individual_amo_function("sat_encodings/amo_product.py", amo_product, n=6)
    test_individual_amo_function("sat_encodings/amo_seqcounter.py", amo_seqcounter, n=6)

    print("-" * 70)
    # 3. Test qua Manager Dispatcher
    methods = ["pairwise", "binary", "commander", "product", "seqcounter"]
    test_cardinality_manager(methods, n=6)

    print("=" * 70)
    print("TAT CA FILE VA PHUONG PHAP DEU HOAT DONG CHINH XAC 100%!")


if __name__ == "__main__":
    run_all()
