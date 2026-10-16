"""
Sudoku Solver bằng Gurobi Optimizer (MIP / Integer Programming).
Hỗ trợ giải Sudoku kích thước tổng quát N x N.
"""

from typing import Optional, List
import gurobipy as gp
from gurobipy import GRB
from utils import DEFAULT_GRID, print_grid, get_grid_params


def solve_sudoku_gurobi(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku N x N bằng Gurobi Optimizer (MIP)."""
    N, br, bc = get_grid_params(initial_grid)

    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()

    model = gp.Model("Sudoku_Gurobi", env=env)

    # 1. N x N x N biến nhị phân x[r, c, v] in {0, 1}
    x = model.addVars(N, N, range(1, N + 1), vtype=GRB.BINARY, name="x")

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(N):
        for c in range(N):
            val = initial_grid[r][c]
            if val != 0:
                model.addConstr(x[r, c, val] == 1, name=f"Clue_{r}_{c}")

    # 3. Mỗi ô (r, c) nhận đúng 1 giá trị
    for r in range(N):
        for c in range(N):
            model.addConstr(x.sum(r, c, "*") == 1, name=f"Cell_{r}_{c}")

    # 4. Mỗi hàng r chứa giá trị v đúng 1 lần
    for r in range(N):
        for v in range(1, N + 1):
            model.addConstr(x.sum(r, "*", v) == 1, name=f"Row_{r}_{v}")

    # 5. Mỗi cột c chứa giá trị v đúng 1 lần
    for c in range(N):
        for v in range(1, N + 1):
            model.addConstr(x.sum("*", c, v) == 1, name=f"Col_{c}_{v}")

    # 6. Mỗi khối (br x bc) chứa giá trị v đúng 1 lần
    num_block_rows = N // br
    num_block_cols = N // bc
    for block_r_idx in range(num_block_rows):
        for block_c_idx in range(num_block_cols):
            for v in range(1, N + 1):
                model.addConstr(
                    gp.quicksum(
                        x[r, c, v]
                        for r in range(block_r_idx * br, (block_r_idx + 1) * br)
                        for c in range(block_c_idx * bc, (block_c_idx + 1) * bc)
                    ) == 1,
                    name=f"Block_{block_r_idx}_{block_c_idx}_{v}"
                )

    # 7. Tối ưu hóa
    model.optimize()

    # 8. Trích xuất nghiệm
    solved_grid = None
    if model.status == GRB.OPTIMAL:
        solved_grid = [[0 for _ in range(N)] for _ in range(N)]
        for r in range(N):
            for c in range(N):
                for v in range(1, N + 1):
                    if x[r, c, v].X > 0.5:
                        solved_grid[r][c] = v
                        break

    env.dispose()
    return solved_grid


if __name__ == "__main__":
    solution = solve_sudoku_gurobi(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG GUROBI OPTIMIZER")
    else:
        print("Khong tim thay nghiem.")
