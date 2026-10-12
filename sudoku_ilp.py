"""
Facade wrapper tương thích ngược trỏ tới solvers.ilp_solver.
"""

from solvers.ilp_solver import solve_sudoku_ilp
from utils import DEFAULT_GRID, print_grid

if __name__ == "__main__":
    solution = solve_sudoku_ilp(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG ILP (PuLP / CBC)")
    else:
        print("Khong tim thay nghiem.")
