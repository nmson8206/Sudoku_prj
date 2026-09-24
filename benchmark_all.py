import sys
import time

from encoding import sudoku_solve as solve_sat, decode_model
from sudoku_cpsat import solve_sudoku_cpsat
from sudoku_cplex_cp import solve_sudoku_cplex_cp
from sudoku_gurobi import solve_sudoku_gurobi
from sudoku_cplex_mip import solve_sudoku_cplex_mip

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]


def run_benchmark():
    solvers = [
        ("SAT (Glucose3)", lambda g: decode_model(solve_sat(g))),
        ("CP-SAT (Google OR-Tools)", solve_sudoku_cpsat),
        ("CPLEX CP (IBM CP Optimizer)", solve_sudoku_cplex_cp),
        ("Gurobi (MIP)", solve_sudoku_gurobi),
        ("CPLEX MIP (IBM CPLEX)", solve_sudoku_cplex_mip),
    ]

    print("=" * 65)
    print(f"{'SOLVER':<30} | {'STATUS':<12} | {'THOI GIAN (ms)':<15}")
    print("=" * 65)

    for name, func in solvers:
        t0 = time.perf_counter()
        res = func(grid)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        status = "Thanh cong" if res else "That bai"
        print(f"{name:<30} | {status:<12} | {elapsed_ms:>10.2f} ms")

    print("=" * 65)


if __name__ == "__main__":
    run_benchmark()
