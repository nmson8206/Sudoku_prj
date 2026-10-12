"""
Facade wrapper tương thích ngược trỏ tới solvers.cplex_cp_solver.
"""

from solvers.cplex_cp_solver import solve_sudoku_cplex_cp
from utils import DEFAULT_GRID, print_grid

if __name__ == "__main__":
    solution = solve_sudoku_cplex_cp(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG IBM CPLEX CP (CP OPTIMIZER)")
    else:
        print("Khong tim thay nghiem.")
