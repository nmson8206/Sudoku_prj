import sys
from ortools.sat.python import cp_model

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


def solve_sudoku_cp(initial_grid):
    """
    Giải Sudoku bằng phương pháp Constraint Programming (CP)
    sử dụng OR-Tools CP-SAT Model.
    """
    model = cp_model.CpModel()

    # 1. Khai báo 81 biến nguyên x[r][c] với miền giá trị từ 1 đến 9
    cells = {}
    for r in range(9):
        for c in range(9):
            cells[r, c] = model.new_int_var(1, 9, f"cell_{r}_{c}")

    # 2. Ràng buộc gợi ý ban đầu (Initial Clues)
    for r in range(9):
        for c in range(9):
            val = initial_grid[r][c]
            if val != 0:
                model.add(cells[r, c] == val)

    # 3. Ràng buộc hàng: mỗi hàng chứa các số khác nhau từng đôi một
    for r in range(9):
        model.add_all_different([cells[r, c] for c in range(9)])

    # 4. Ràng buộc cột: mỗi cột chứa các số khác nhau từng đôi một
    for c in range(9):
        model.add_all_different([cells[r, c] for r in range(9)])

    # 5. Ràng buộc khối 3x3: mỗi khối chứa các số khác nhau từng đôi một
    for br in range(3):
        for bc in range(3):
            block_cells = [
                cells[r, c]
                for r in range(br * 3, br * 3 + 3)
                for c in range(bc * 3, bc * 3 + 3)
            ]
            model.add_all_different(block_cells)

    # 6. Giải bài toán
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solved_grid = [[solver.value(cells[r, c]) for c in range(9)] for r in range(9)]
        return solved_grid
    return None


if __name__ == "__main__":
    solution = solve_sudoku_cp(grid)
    if solution:
        print("=== KET QUA GIAI BANG CP (CONSTRAINT PROGRAMMING) ===")
        for row in solution:
            print(row)
    else:
        print("Khong tim thay nghiem.")
