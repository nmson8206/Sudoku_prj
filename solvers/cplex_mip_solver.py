"""
Sudoku Solver bằng IBM CPLEX MIP (Mixed-Integer Programming).
"""

from typing import Optional, List
from docplex.mp.model import Model
from utils import DEFAULT_GRID, print_grid


def solve_sudoku_cplex_mip(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku bằng IBM CPLEX MIP."""
    mdl = Model(name="Sudoku_CPLEX_MIP")

    # 1. 729 biến nhị phân x[r, c, v] in {0, 1}
    x = mdl.binary_var_dict(
        ((r, c, v) for r in range(9) for c in range(9) for v in range(1, 10)),
        name="x"
    )

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                mdl.add_constraint(x[r, c, val] == 1)

    # 3. Mỗi ô (r, c) nhận đúng 1 giá trị
    for r in range(9):
        for c in range(9):
            mdl.add_constraint(mdl.sum(x[r, c, v] for v in range(1, 10)) == 1)

    # 4. Mỗi hàng r chứa giá trị v đúng 1 lần
    for r in range(9):
        for v in range(1, 10):
            mdl.add_constraint(mdl.sum(x[r, c, v] for c in range(9)) == 1)

    # 5. Mỗi cột c chứa giá trị v đúng 1 lần
    for c in range(9):
        for v in range(1, 10):
            mdl.add_constraint(mdl.sum(x[r, c, v] for r in range(9)) == 1)

    # 6. Mỗi khối 3x3 chứa giá trị v đúng 1 lần
    for br in range(3):
        for bc in range(3):
            for v in range(1, 10):
                mdl.add_constraint(
                    mdl.sum(
                        x[r, c, v]
                        for r in range(br * 3, br * 3 + 3)
                        for c in range(bc * 3, bc * 3 + 3)
                    ) == 1
                )

    # 7. Giải mô hình
    sol = mdl.solve(log_output=False)

    if sol:
        solved_grid = [[0 for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                for v in range(1, 10):
                    if sol[x[r, c, v]] >= 0.5:
                        solved_grid[r][c] = v
                        break
        return solved_grid
    return None


if __name__ == "__main__":
    solution = solve_sudoku_cplex_mip(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG IBM CPLEX MIP")
    else:
        print("Khong tim thay nghiem.")
