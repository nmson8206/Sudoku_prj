"""
Sudoku Solver bằng Google OR-Tools CP-SAT (Constraint Programming).
Hỗ trợ giải Sudoku kích thước tổng quát N x N.
"""

from typing import Optional, List
from ortools.sat.python import cp_model
from utils import DEFAULT_GRID, print_grid, get_grid_params


def solve_sudoku_cpsat(initial_grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Giải Sudoku N x N bằng Google OR-Tools CP-SAT."""
    N, br, bc = get_grid_params(initial_grid)
    model = cp_model.CpModel()

    # 1. N x N biến nguyên cell[r, c] với miền giá trị [1..N]
    cells = {}
    for r in range(N):
        for c in range(N):
            cells[r, c] = model.new_int_var(1, N, f"cell_{r}_{c}")

    # 2. Ràng buộc các ô có sẵn (Clues)
    for r in range(N):
        for c in range(N):
            val = initial_grid[r][c]
            if val != 0:
                model.add(cells[r, c] == val)

    # 3. Ràng buộc AllDifferent cho mỗi hàng
    for r in range(N):
        model.add_all_different([cells[r, c] for c in range(N)])

    # 4. Ràng buộc AllDifferent cho mỗi cột
    for c in range(N):
        model.add_all_different([cells[r, c] for r in range(N)])

    # 5. Ràng buộc AllDifferent cho mỗi khối (br x bc)
    num_block_rows = N // br
    num_block_cols = N // bc
    for block_r_idx in range(num_block_rows):
        for block_c_idx in range(num_block_cols):
            block_cells = [
                cells[r, c]
                for r in range(block_r_idx * br, (block_r_idx + 1) * br)
                for c in range(block_c_idx * bc, (block_c_idx + 1) * bc)
            ]
            model.add_all_different(block_cells)

    # 6. Giải bằng CpSolver
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = False
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [[solver.value(cells[r, c]) for c in range(N)] for r in range(N)]
    return None


if __name__ == "__main__":
    solution = solve_sudoku_cpsat(DEFAULT_GRID)
    if solution:
        print_grid(solution, "GIAI SUDOKU BANG GOOGLE OR-TOOLS CP-SAT")
    else:
        print("Khong tim thay nghiem.")
