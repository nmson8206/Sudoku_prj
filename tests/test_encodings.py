"""
Unit tests kiểm tra tính đúng đắn (soundness & completeness) của các phương pháp ALO, AMO và EO.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from itertools import product as iter_product
from pysat.solvers import Glucose3

from sat_encodings import (
    at_least_one,
    amo_pairwise,
    amo_binary,
    amo_commander,
    amo_product,
    amo_seqcounter,
    at_most_one,
    exactly_one,
)


def verify_amo(name: str, fn, n: int = 6):
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
        assert is_sat == expected, f"Lỗi tại {name}: assignment={assignment}"

    print(f"[PASSED] AMO {name:<16} (n={n}) - 100% {2**n} cases.")


def verify_alo(n: int = 6):
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
        assert is_sat == expected, f"Lỗi tại ALO: assignment={assignment}"

    print(f"[PASSED] ALO {'standard':<16} (n={n}) - 100% {2**n} cases.")


def verify_eo(methods: list[str], n: int = 6):
    lits = list(range(1, n + 1))
    for m in methods:
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
            assert is_sat == expected, f"Lỗi tại EO-{m}"
        print(f"[PASSED] EO  {m:<16} (n={n}) - 100% {2**n} cases.")


def run_all():
    print("=" * 64)
    print("TEST SUITE: ENCODINGS (ALO, AMO, EO)")
    print("=" * 64)
    verify_alo(n=6)
    verify_amo("pairwise", amo_pairwise, n=6)
    verify_amo("binary", amo_binary, n=6)
    verify_amo("commander", amo_commander, n=6)
    verify_amo("product", amo_product, n=6)
    verify_amo("seqcounter", amo_seqcounter, n=6)
    print("-" * 64)
    verify_eo(["pairwise", "binary", "commander", "product", "seqcounter"], n=6)
    print("=" * 64)


if __name__ == "__main__":
    run_all()
