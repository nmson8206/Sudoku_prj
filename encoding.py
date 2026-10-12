"""
Facade wrapper tương thích ngược trỏ tới solvers.sat_solver.
"""

from solvers.sat_solver import (
    var,
    cell_variables,
    row_variables,
    column_variables,
    block_variables,
    encode_sudoku,
    decode_model,
    solve_sudoku_sat as sudoku_solve,
)
from utils import DEFAULT_GRID, print_grid

if __name__ == "__main__":
    for method in ["pairwise", "binary", "commander", "product", "seqcounter"]:
        print(f"\n--- Testing SAT method: {method.upper()} ---")
        solution = sudoku_solve(DEFAULT_GRID, method=method)
        if solution:
            print_grid(solution, f"GIAI SUDOKU BANG SAT ({method})")
        else:
            print("Khong tim thay nghiem.")
