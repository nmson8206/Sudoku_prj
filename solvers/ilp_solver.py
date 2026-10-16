"""
Sudoku Solver bằng quy hoạch nguyên tuyến tính (ILP / 0-1 Integer Programming)
sử dụng thư viện PuLP (mặc định CBC Solver).
Hỗ trợ giải Sudoku kích thước tổng quát N x N.
"""

from typing import Optional, List
import pulp
from utils import DEFAULT_GRID, print_grid, get_grid_params


def solve_sudoku_ilp(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku N x N bằng ILP (PuLP / CBC)."""
    N, br, bc = get_grid_params(initial_grid)
    prob = pulp.LpProblem("Sudoku_ILP", pulp.LpMinimize)

    # 1. N x N x N biến nhị phân x[r, c, v] in {0, 1}
    x = pulp.LpVariable.dicts(
        "x",
        ((r, c, v) for r in range(N) for c in range(N) for v in range(1, N + 1)),
        cat=pulp.LpBinary
    )

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(N):
        for c in range(N):
            val = initial_grid[r][c]
            if val != 0:
                prob += x[r, c, val] == 1, f"Clue_{r}_{c}"

    # 3. Mỗi ô (r, c) phải nhận đúng một giá trị
    for r in range(N):
        for c in range(N):
            prob += (
                pulp.lpSum([x[r, c, v] for v in range(1, N + 1)]) == 1,
                f"Cell_OneValue_{r}_{c}"
            )

    # 4. Trong mỗi hàng r, mỗi giá trị v xuất hiện đúng 1 lần
    for r in range(N):
        for v in range(1, N + 1):
            prob += (
                pulp.lpSum([x[r, c, v] for c in range(N)]) == 1,
                f"Row_Unique_{r}_{v}"
            )

    # 5. Trong mỗi cột c, mỗi giá trị v xuất hiện đúng 1 lần
    for c in range(N):
        for v in range(1, N + 1):
            prob += (
                pulp.lpSum([x[r, c, v] for r in range(N)]) == 1,
                f"Col_Unique_{c}_{v}"
            )

    # 6. Trong mỗi khối (br x bc), mỗi giá trị v xuất hiện đúng 1 lần
    num_block_rows = N // br
    num_block_cols = N // bc
    for block_r_idx in range(num_block_rows):
        for block_c_idx in range(num_block_cols):
            for v in range(1, N + 1):
                prob += (
                    pulp.lpSum([
                        x[r, c, v]
                        for r in range(block_r_idx * br, (block_r_idx + 1) * br)
                        for c in range(block_c_idx * bc, (block_c_idx + 1) * bc)
                    ]) == 1,
                    f"Block_Unique_{block_r_idx}_{block_c_idx}_{v}"
                )

    # 7. Giải bài toán (ẩn log solver)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # 8. Trích xuất nghiệm
    if prob.status == pulp.constants.LpStatusOptimal:
        solved_grid = [[0 for _ in range(N)] for _ in range(N)]
        for r in range(N):
            for c in range(N):
                for v in range(1, N + 1):
                    if pulp.value(x[r, c, v]) == 1:
                        solved_grid[r][c] = v
                        break
        return solved_grid
    return None


if __name__ == "__main__":
    solution = solve_sudoku_ilp(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG ILP (PuLP / CBC)")
    else:
        print("Khong tim thay nghiem.")
