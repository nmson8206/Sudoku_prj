"""
Facade wrapper tương thích ngược trỏ tới solvers.gurobi_solver.
"""

from solvers.gurobi_solver import solve_sudoku_gurobi
from utils import DEFAULT_GRID, print_grid

if __name__ == "__main__":
    solution = solve_sudoku_gurobi(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG GUROBI OPTIMIZER")
    else:
        print("Khong tim thay nghiem.")
