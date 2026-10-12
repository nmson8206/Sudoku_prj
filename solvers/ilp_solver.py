"""
Sudoku Solver bằng quy hoạch nguyên tuyến tính (ILP / 0-1 Integer Programming)
sử dụng thư viện PuLP (mặc định CBC Solver).
"""

from typing import Optional, List
import pulp
from utils import DEFAULT_GRID, print_grid


def solve_sudoku_ilp(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku bằng ILP (PuLP / CBC)."""
    prob = pulp.LpProblem("Sudoku_ILP", pulp.LpMinimize)

    # 1. 729 biến nhị phân x[r, c, v] in {0, 1}
    x = pulp.LpVariable.dicts(
        "x",
        ((r, c, v) for r in range(9) for c in range(9) for v in range(1, 10)),
        cat=pulp.LpBinary
    )

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                prob += x[r, c, val] == 1, f"Clue_{r}_{c}"

    # 3. Mỗi ô (r, c) phải nhận đúng một giá trị
    for r in range(9):
        for c in range(9):
            prob += (
                pulp.lpSum([x[r, c, v] for v in range(1, 10)]) == 1,
                f"Cell_OneValue_{r}_{c}"
            )

    # 4. Trong mỗi hàng r, mỗi giá trị v xuất hiện đúng 1 lần
    for r in range(9):
        for v in range(1, 10):
            prob += (
                pulp.lpSum([x[r, c, v] for c in range(9)]) == 1,
                f"Row_Unique_{r}_{v}"
            )

    # 5. Trong mỗi cột c, mỗi giá trị v xuất hiện đúng 1 lần
    for c in range(9):
        for v in range(1, 10):
            prob += (
                pulp.lpSum([x[r, c, v] for r in range(9)]) == 1,
                f"Col_Unique_{c}_{v}"
            )

    # 6. Trong mỗi khối 3x3, mỗi giá trị v xuất hiện đúng 1 lần
    for br in range(3):
        for bc in range(3):
            for v in range(1, 10):
                prob += (
                    pulp.lpSum([
                        x[r, c, v]
                        for r in range(br * 3, br * 3 + 3)
                        for c in range(bc * 3, bc * 3 + 3)
                    ]) == 1,
                    f"Block_Unique_{br}_{bc}_{v}"
                )

    # 7. Giải bài toán (ẩn log solver)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # 8. Trích xuất nghiệm
    if prob.status == pulp.constants.LpStatusOptimal:
        solved_grid = [[0 for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                for v in range(1, 10):
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
