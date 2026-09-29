import gurobipy as gp
from gurobipy import GRB
from utils import DEFAULT_GRID, print_grid


def solve_sudoku_gurobi(initial_grid):
    """
    Giai Sudoku bang Gurobi Optimizer (MIP / Integer Programming).
    """
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()

    model = gp.Model("Sudoku_Gurobi", env=env)

    # 1. 729 bien nhi phan x[r, c, v] in {0, 1}
    x = model.addVars(9, 9, range(1, 10), vtype=GRB.BINARY, name="x")

    # 2. Rang buoc cac o co san (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                model.addConstr(x[r, c, val] == 1, name=f"Clue_{r}_{c}")

    # 3. Moi o (r, c) nhan dung 1 gia tri tu 1 den 9
    for r in range(9):
        for c in range(9):
            model.addConstr(x.sum(r, c, "*") == 1, name=f"Cell_{r}_{c}")

    # 4. Moi hang r chua gia tri v dung 1 lan
    for r in range(9):
        for v in range(1, 10):
            model.addConstr(x.sum(r, "*", v) == 1, name=f"Row_{r}_{v}")

    # 5. Moi cot c chua gia tri v dung 1 lan
    for c in range(9):
        for v in range(1, 10):
            model.addConstr(x.sum("*", c, v) == 1, name=f"Col_{c}_{v}")

    # 6. Moi khoi 3x3 chua gia tri v dung 1 lan
    for br in range(3):
        for bc in range(3):
            for v in range(1, 10):
                model.addConstr(
                    gp.quicksum(
                        x[r, c, v]
                        for r in range(br * 3, br * 3 + 3)
                        for c in range(bc * 3, bc * 3 + 3)
                    ) == 1,
                    name=f"Block_{br}_{bc}_{v}"
                )

    # 7. Tien hanh toi uu hoa
    model.optimize()

    # 8. Trich xuat nghiem neu tim thay
    solved_grid = None
    if model.status == GRB.OPTIMAL:
        solved_grid = [[0 for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                for v in range(1, 10):
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
