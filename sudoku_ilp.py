import sys
import pulp

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]


def solve_sudoku_ilp(initial_grid):
    """
    Giải Sudoku bằng quy hoạch nguyên tuyến tính (ILP / 0-1 Integer Programming)
    sử dụng thư viện PuLP.
    """
    # Khởi tạo bài toán (không cần hàm mục tiêu vì chỉ cần tìm nghiệm khả thi)
    prob = pulp.LpProblem("Sudoku_ILP", pulp.LpMinimize)

    # 1. Khai báo 9x9x9 = 729 biến nhị phân x[r, c, v] in {0, 1}
    # x[r, c, v] = 1 nếu ô (r, c) nhận giá trị v, ngược lại = 0
    x = pulp.LpVariable.dicts(
        "x",
        ((r, c, v) for r in range(9) for c in range(9) for v in range(1, 10)),
        cat=pulp.LpBinary
    )

    # 2. Ràng buộc gợi ý ban đầu (Initial Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                prob += x[r, c, val] == 1, f"Clue_{r}_{c}"

    # 3. Mỗi ô (r, c) phải nhận đúng một giá trị v trong [1..9]
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

    # 7. Giải bài toán ILP (tắt in log mặc định của solver)
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
    solution = solve_sudoku_ilp(grid)
    if solution:
        print("=== KET QUA GIAI BANG ILP (INTEGER LINEAR PROGRAMMING) ===")
        for row in solution:
            print(row)
    else:
        print("Khong tim thay nghiem.")
