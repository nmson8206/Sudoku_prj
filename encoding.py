from pysat.solvers import Glucose3
from utils import DEFAULT_GRID, print_grid
from sat_encodings import exactly_one, AVAILABLE_METHODS


def var(r, c, d):
    return 81 * r + 9 * c + d


def cell_variables(r, c) -> list[int]:
    return [var(r, c, d) for d in range(1, 10)]


def row_variables(r, d) -> list[int]:
    return [var(r, c, d) for c in range(9)]


def column_variables(c, d) -> list[int]:
    return [var(r, c, d) for r in range(9)]


def block_variables(r, c, d) -> list[int]:
    return [
        var(br, bc, d)
        for br in range(r * 3, r * 3 + 3)
        for bc in range(c * 3, c * 3 + 3)
    ]


def encode_cell_constraints(method: str = "pairwise", top_id: int = 729):
    clauses = []
    curr_top = top_id
    for r in range(9):
        for c in range(9):
            cls, curr_top = exactly_one(cell_variables(r, c), method=method, top_id=curr_top)
            clauses += cls
    return clauses, curr_top


def encode_block_constraints(method: str = "pairwise", top_id: int = 729):
    clauses = []
    curr_top = top_id
    for r in range(3):
        for c in range(3):
            for d in range(1, 10):
                cls, curr_top = exactly_one(block_variables(r, c, d), method=method, top_id=curr_top)
                clauses += cls
    return clauses, curr_top


def encode_row_constraints(method: str = "pairwise", top_id: int = 729):
    clauses = []
    curr_top = top_id
    for r in range(9):
        for d in range(1, 10):
            cls, curr_top = exactly_one(row_variables(r, d), method=method, top_id=curr_top)
            clauses += cls
    return clauses, curr_top


def encode_column_constraints(method: str = "pairwise", top_id: int = 729):
    clauses = []
    curr_top = top_id
    for c in range(9):
        for d in range(1, 10):
            cls, curr_top = exactly_one(column_variables(c, d), method=method, top_id=curr_top)
            clauses += cls
    return clauses, curr_top


def encode_clues(grid) -> list[list[int]]:
    clauses = []
    for r in range(9):
        for c in range(9):
            d = grid[r][c]
            if d != 0:
                clauses.append([var(r, c, d)])
    return clauses


def encode_sudoku(grid, method: str = "pairwise") -> list[list[int]]:
    clauses = []
    top_id = 729  # 81 ô x 9 chữ số = 729 biến nguyên bản của Sudoku

    row_cls, top_id = encode_row_constraints(method=method, top_id=top_id)
    col_cls, top_id = encode_column_constraints(method=method, top_id=top_id)
    blk_cls, top_id = encode_block_constraints(method=method, top_id=top_id)
    cel_cls, top_id = encode_cell_constraints(method=method, top_id=top_id)

    clauses += row_cls
    clauses += col_cls
    clauses += blk_cls
    clauses += cel_cls
    clauses += encode_clues(grid)
    return clauses


def sudoku_solve(grid, method: str = "pairwise"):
    clauses = encode_sudoku(grid, method=method)
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        return solver.get_model()
    return None


def decode_model(model):
    if not model:
        return None
    grid = [[0 for _ in range(9)] for _ in range(9)]
    for x in model:
        # Chỉ lấy các biến Sudoku ban đầu (1 đến 729)
        # Các biến phụ sinh ra cho AMO (id > 729) được bỏ qua
        if 1 <= x <= 729:
            x -= 1
            r = x // 81
            rem = x % 81
            c = rem // 9
            d = rem % 9 + 1
            grid[r][c] = d
    return grid


if __name__ == "__main__":
    for method in ["pairwise", "binary", "commander", "product", "seqcounter"]:
        print(f"\n--- Testing SAT method: {method.upper()} ---")
        model = sudoku_solve(DEFAULT_GRID, method=method)
        if model:
            solution = decode_model(model)
            print_grid(solution, f"GIAI SUDOKU BANG SAT ({method})")
        else:
            print("Khong tim thay nghiem.")
