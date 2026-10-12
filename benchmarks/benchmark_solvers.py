"""
Script đo lường và so sánh hiệu năng của tất cả các Solver giải Sudoku:
- SAT (Glucose3 với đầy đủ 5 phương pháp mã hóa: Pairwise, Binary, Commander, Product, SeqCounter)
- CP-SAT (Google OR-Tools)
- ILP (PuLP / CBC)
- CPLEX CP (IBM CP Optimizer)
- Gurobi (MIP)
- CPLEX MIP (IBM CPLEX)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import time
from utils import DEFAULT_GRID
from solvers import (
    solve_sudoku_sat,
    solve_sudoku_cpsat,
    solve_sudoku_ilp,
    solve_sudoku_cplex_cp,
    solve_sudoku_gurobi,
    solve_sudoku_cplex_mip,
)


def run_benchmark():
    solvers = [
        # Nhánh SAT (Glucose3) với đầy đủ 5 kỹ thuật mã hóa Cardinality (AMO)
        ("SAT (Glucose3 - Pairwise)", lambda g: solve_sudoku_sat(g, method="pairwise")),
        ("SAT (Glucose3 - Binary)", lambda g: solve_sudoku_sat(g, method="binary")),
        ("SAT (Glucose3 - Commander)", lambda g: solve_sudoku_sat(g, method="commander")),
        ("SAT (Glucose3 - Product)", lambda g: solve_sudoku_sat(g, method="product")),
        ("SAT (Glucose3 - SeqCounter)", lambda g: solve_sudoku_sat(g, method="seqcounter")),

        # Nhánh Constraint Programming (CP)
        ("CP-SAT (Google OR-Tools)", solve_sudoku_cpsat),
        ("CPLEX CP (IBM CP Optimizer)", solve_sudoku_cplex_cp),

        # Nhánh Integer Linear Programming (ILP / MIP)
        ("ILP (PuLP / CBC)", solve_sudoku_ilp),
        ("Gurobi (MIP Optimizer)", solve_sudoku_gurobi),
        ("CPLEX MIP (IBM CPLEX)", solve_sudoku_cplex_mip),
    ]

    print("=" * 76)
    print(f"{'SOLVER':<35} | {'STATUS':<14} | {'THỜI GIAN (ms)':<18}")
    print("=" * 76)

    for name, func in solvers:
        try:
            t0 = time.perf_counter()
            res = func(DEFAULT_GRID)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            status = "Thành công" if res else "Thất bại"
            print(f"{name:<35} | {status:<14} | {elapsed_ms:>13.2f} ms")
        except Exception as e:
            print(f"{name:<35} | {'Lỗi runtime':<14} | {'N/A':>16}")

    print("=" * 76)


if __name__ == "__main__":
    run_benchmark()
