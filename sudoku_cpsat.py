"""
Facade wrapper tương thích ngược trỏ tới solvers.cpsat_solver.
"""

from solvers.cpsat_solver import solve_sudoku_cpsat
from utils import DEFAULT_GRID, print_grid

if __name__ == "__main__":
    solution = solve_sudoku_cpsat(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG GOOGLE OR-TOOLS CP-SAT")
    else:
        print("Khong tim thay nghiem.")
