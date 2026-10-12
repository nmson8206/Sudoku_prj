"""
Facade wrapper tương thích ngược trỏ tới solvers.cplex_mip_solver.
"""

from solvers.cplex_mip_solver import solve_sudoku_cplex_mip
from utils import DEFAULT_GRID, print_grid

if __name__ == "__main__":
    solution = solve_sudoku_cplex_mip(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG IBM CPLEX MIP")
    else:
        print("Khong tim thay nghiem.")
