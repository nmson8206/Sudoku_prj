from docplex.mp.model import Model
from utils import DEFAULT_GRID, print_grid


def solve_sudoku_cplex_mip(initial_grid):
    """
    Giai Sudoku bang IBM CPLEX MIP (Mixed-Integer Programming).
    """
    mdl = Model(name="Sudoku_CPLEX_MIP")

    # 1. 729 bien nhi phan x[r, c, v] in {0, 1}
    x = mdl.binary_var_dict(
        ((r, c, v) for r in range(9) for c in range(9) for v in range(1, 10)),
        name="x"
    )

    # 2. Rang buoc cac o co san (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                mdl.add_constraint(x[r, c, val] == 1)

    # 3. Moi o (r, c) nhan dung 1 gia tri
    for r in range(9):
        for c in range(9):
            mdl.add_constraint(mdl.sum(x[r, c, v] for v in range(1, 10)) == 1)

    # 4. Moi hang r chua gia tri v dung 1 lan
    for r in range(9):
        for v in range(1, 10):
            mdl.add_constraint(mdl.sum(x[r, c, v] for c in range(9)) == 1)

    # 5. Moi cot c chua gia tri v dung 1 lan
    for c in range(9):
        for v in range(1, 10):
            mdl.add_constraint(mdl.sum(x[r, c, v] for r in range(9)) == 1)

    # 6. Moi khoi 3x3 chua gia tri v dung 1 lan
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

    # 7. Giai mo hinh (tat nhat ky log)
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
