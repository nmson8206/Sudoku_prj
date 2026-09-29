from docplex.cp.model import CpoModel, all_diff
from utils import DEFAULT_GRID, print_grid


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
        return [[sol[cells[r, c]] for c in range(9)] for r in range(9)]
    return None


if __name__ == "__main__":
    solution = solve_sudoku_cplex_cp(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG IBM CPLEX CP (CP OPTIMIZER)")
    else:
        print("Khong tim thay nghiem.")
