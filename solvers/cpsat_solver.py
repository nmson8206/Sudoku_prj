"""
Sudoku Solver bằng Google OR-Tools CP-SAT (Constraint Programming).
"""

from typing import Optional, List
from ortools.sat.python import cp_model
from utils import DEFAULT_GRID, print_grid


def solve_sudoku_cpsat(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku bằng Google OR-Tools CP-SAT."""
    model = cp_model.CpModel()

    # 1. 81 biến nguyên cell[r, c] với miền giá trị [1..9]
    cells = {}
    for r in range(9):
        for c in range(9):
            cells[r, c] = model.new_int_var(1, 9, f"cell_{r}_{c}")

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                model.add(cells[r, c] == val)

    # 3. Ràng buộc AllDifferent cho mỗi hàng
    for r in range(9):
        model.add_all_different([cells[r, c] for c in range(9)])

    # 4. Ràng buộc AllDifferent cho mỗi cột
    for c in range(9):
        model.add_all_different([cells[r, c] for r in range(9)])

    # 5. Ràng buộc AllDifferent cho mỗi khối 3x3
    for br in range(3):
        for bc in range(3):
            block_cells = [
                cells[r, c]
                for r in range(br * 3, br * 3 + 3)
                for c in range(bc * 3, bc * 3 + 3)
            ]
            model.add_all_different(block_cells)

    # 6. Giải bằng CpSolver
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = False
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [[solver.value(cells[r, c]) for c in range(9)] for r in range(9)]
    return None


if __name__ == "__main__":
    solution = solve_sudoku_cpsat(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG GOOGLE OR-TOOLS CP-SAT")
    else:
        print("Khong tim thay nghiem.")
