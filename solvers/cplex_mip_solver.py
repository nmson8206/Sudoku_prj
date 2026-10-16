"""
Sudoku Solver bằng IBM CPLEX MIP (Mixed-Integer Programming).
Hỗ trợ giải Sudoku kích thước tổng quát N x N.
"""

from typing import Optional, List
from docplex.mp.model import Model
from utils import DEFAULT_GRID, print_grid, get_grid_params


def solve_sudoku_cplex_mip(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku N x N bằng IBM CPLEX MIP."""
    N, br, bc = get_grid_params(initial_grid)
    mdl = Model(name="Sudoku_CPLEX_MIP")

    # 1. N x N x N biến nhị phân x[r, c, v] in {0, 1}
    x = mdl.binary_var_dict(
        ((r, c, v) for r in range(N) for c in range(N) for v in range(1, N + 1)),
        name="x"
    )

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(N):
        for c in range(N):
            val = initial_grid[r][c]
            if val != 0:
                mdl.add_constraint(x[r, c, val] == 1)

    # 3. Mỗi ô (r, c) nhận đúng 1 giá trị
    for r in range(N):
        for c in range(N):
            mdl.add_constraint(mdl.sum(x[r, c, v] for v in range(1, N + 1)) == 1)

    # 4. Mỗi hàng r chứa giá trị v đúng 1 lần
    for r in range(N):
        for v in range(1, N + 1):
            mdl.add_constraint(mdl.sum(x[r, c, v] for c in range(N)) == 1)

    # 5. Mỗi cột c chứa giá trị v đúng 1 lần
    for c in range(N):
        for v in range(1, N + 1):
            mdl.add_constraint(mdl.sum(x[r, c, v] for r in range(N)) == 1)

    # 6. Mỗi khối (br x bc) chứa giá trị v đúng 1 lần
    num_block_rows = N // br
    num_block_cols = N // bc
    for block_r_idx in range(num_block_rows):
        for block_c_idx in range(num_block_cols):
            for v in range(1, N + 1):
                mdl.add_constraint(
                    mdl.sum(
                        x[r, c, v]
                        for r in range(block_r_idx * br, (block_r_idx + 1) * br)
                        for c in range(block_c_idx * bc, (block_c_idx + 1) * bc)
                    ) == 1
                )

    # 7. Giải mô hình
    sol = mdl.solve(log_output=False)

    if sol:
        solved_grid = [[0 for _ in range(N)] for _ in range(N)]
        for r in range(N):
            for c in range(N):
                for v in range(1, N + 1):
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
