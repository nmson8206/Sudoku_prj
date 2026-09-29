import pulp
from utils import DEFAULT_GRID, print_grid


def solve_sudoku_ilp(initial_grid):
    """
    Giai Sudoku bang quy hoach nguyen tuyen tinh (ILP / 0-1 Integer Programming)
    su dung thu vien PuLP (CBC Solver).
    """
    prob = pulp.LpProblem("Sudoku_ILP", pulp.LpMinimize)

    # 1. 729 bien nhi phan x[r, c, v] in {0, 1}
    x = pulp.LpVariable.dicts(
        "x",
        ((r, c, v) for r in range(9) for c in range(9) for v in range(1, 10)),
        cat=pulp.LpBinary
    )

    # 2. Rang buoc cac o co san (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                prob += x[r, c, val] == 1, f"Clue_{r}_{c}"

    # 3. Moi o (r, c) phai nhan dung mot gia tri
    for r in range(9):
        for c in range(9):
            prob += (
                pulp.lpSum([x[r, c, v] for v in range(1, 10)]) == 1,
                f"Cell_OneValue_{r}_{c}"
            )

    # 4. Trong moi hang r, moi gia tri v xuat hien dung 1 lan
    for r in range(9):
        for v in range(1, 10):
            prob += (
                pulp.lpSum([x[r, c, v] for c in range(9)]) == 1,
                f"Row_Unique_{r}_{v}"
            )

    # 5. Trong moi cot c, moi gia tri v xuat hien dung 1 lan
    for c in range(9):
        for v in range(1, 10):
            prob += (
                pulp.lpSum([x[r, c, v] for r in range(9)]) == 1,
                f"Col_Unique_{c}_{v}"
            )

    # 6. Trong moi khoi 3x3, moi gia tri v xuat hien dung 1 lan
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

    # 7. Giai bai toan (an log solver)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # 8. Trich xuat nghiem
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
