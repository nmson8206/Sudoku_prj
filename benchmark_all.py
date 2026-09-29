import time
from utils import DEFAULT_GRID

# Import các solver
from encoding import sudoku_solve as solve_sat, decode_model
from sudoku_cpsat import solve_sudoku_cpsat
from sudoku_ilp import solve_sudoku_ilp
from sudoku_cplex_cp import solve_sudoku_cplex_cp
from sudoku_gurobi import solve_sudoku_gurobi
from sudoku_cplex_mip import solve_sudoku_cplex_mip


def run_benchmark():
    solvers = [
        ("SAT (Glucose3)", lambda g: decode_model(solve_sat(g))),
        ("CP-SAT (Google OR-Tools)", solve_sudoku_cpsat),
        ("ILP (PuLP / CBC)", solve_sudoku_ilp),
        ("CPLEX CP (IBM CP Optimizer)", solve_sudoku_cplex_cp),
        ("Gurobi (MIP)", solve_sudoku_gurobi),
        ("CPLEX MIP (IBM CPLEX)", solve_sudoku_cplex_mip),
    ]

    print("=" * 68)
    print(f"{'SOLVER':<30} | {'STATUS':<14} | {'THOI GIAN (ms)':<16}")
    print("=" * 68)

    for name, func in solvers:
        try:
            t0 = time.perf_counter()
            res = func(DEFAULT_GRID)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            status = "Thanh cong" if res else "That bai"
            print(f"{name:<30} | {status:<14} | {elapsed_ms:>11.2f} ms")
        except Exception as e:
            print(f"{name:<30} | {'Loi runtime':<14} | {'N/A':>14}")

    print("=" * 68)


if __name__ == "__main__":
    run_benchmark()
