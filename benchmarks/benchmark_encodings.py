"""
Script benchmark so sánh chi tiết 5 phương pháp mã hóa SAT cho Sudoku:
- Pairwise
- Binary (PySAT Bitwise)
- Commander Encoding
- Product Encoding (Chen 2010)
- Sequential Counter (PySAT Sinz 2005)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import time
from utils import DEFAULT_GRID
from solvers.sat_solver import encode_sudoku, decode_model
from pysat.solvers import Glucose3


def benchmark_encodings():
    methods = [
        ("Pairwise (Naive)", "pairwise"),
        ("Binary (PySAT Bitwise)", "binary"),
        ("Commander Encoding", "commander"),
        ("Product Encoding (Chen)", "product"),
        ("Sequential Counter (PySAT)", "seqcounter"),
    ]

    print("=" * 86)
    print(f"{'PHƯƠNG PHÁP':<26} | {'SỐ BIẾN':<10} | {'SỐ CLAUSES':<11} | {'ENCODE(ms)':<11} | {'SOLVE(ms)':<10} | {'TỔNG(ms)':<10}")
    print("=" * 86)

    for label, method_key in methods:
        t0 = time.perf_counter()
        clauses, top_id = encode_sudoku(DEFAULT_GRID, method=method_key)
        t_enc = (time.perf_counter() - t0) * 1000

        solver = Glucose3()
        for cl in clauses:
            solver.add_clause(cl)

        t1 = time.perf_counter()
        solved = solver.solve()
        t_solve = (time.perf_counter() - t1) * 1000

        model = solver.get_model() if solved else None
        res = decode_model(model)
        status = "OK" if (res and res[0][0] == 5) else "FAIL"

        t_total = t_enc + t_solve
        print(f"{label:<26} | {top_id:<10} | {len(clauses):<11} | {t_enc:>9.2f} ms | {t_solve:>8.2f} ms | {t_total:>8.2f} ms")

    print("=" * 86)


if __name__ == "__main__":
    benchmark_encodings()
