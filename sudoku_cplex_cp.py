import sys
from docplex.cp.model import CpoModel, all_diff

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


def solve_sudoku_cplex_cp(initial_grid):
    """
    Giai Sudoku bang CPLEX CP Optimizer (Constraint Programming).
    """
    model = CpoModel(name="Sudoku_CPLEX_CP")

    # 1. 81 bien nguyen cell[r, c] voi mien gia tri [1..9]
    cells = {}
    for r in range(9):
        for c in range(9):
            cells[r, c] = model.integer_var(1, 9, name=f"cell_{r}_{c}")

    # 2. Rang buoc cac o co san (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                model.add(cells[r, c] == val)

    # 3. Rang buoc all_diff cho moi hang
    for r in range(9):
        model.add(all_diff([cells[r, c] for c in range(9)]))

    # 4. Rang buoc all_diff cho moi cot
    for c in range(9):
        model.add(all_diff([cells[r, c] for r in range(9)]))

    # 5. Rang buoc all_diff cho moi khoi 3x3
    for br in range(3):
        for bc in range(3):
            block_cells = [
                cells[r, c]
                for r in range(br * 3, br * 3 + 3)
                for c in range(bc * 3, bc * 3 + 3)
            ]
            model.add(all_diff(block_cells))

    # 6. Giai bai toan (an nhat ky log thong qua LogVerbosity="Quiet")
    sol = model.solve(LogVerbosity="Quiet")

    if sol and sol.is_solution():
        solved_grid = [[sol[cells[r, c]] for c in range(9)] for r in range(9)]
        return solved_grid
    return None


if __name__ == "__main__":
    solution = solve_sudoku_cplex_cp(grid)
    if solution:
        print("=== KET QUA GIAI BANG IBM CPLEX CP (CP OPTIMIZER) ===")
        for row in solution:
            print(row)
    else:
        print("Khong tim thay nghiem.")
