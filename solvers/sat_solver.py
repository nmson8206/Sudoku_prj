"""
Sudoku Solver bằng SAT (sử dụng solver Glucose3 từ thư viện PySAT).
Hỗ trợ chuyển đổi linh hoạt giữa các phương pháp mã hóa cardinality (AMO):
- 'pairwise'
- 'binary'
- 'commander'
- 'product'
- 'seqcounter'
"""

from typing import Optional, List, Tuple
from pysat.solvers import Glucose3
from utils import DEFAULT_GRID, print_grid
from sat_encodings import exactly_one


def var(r: int, c: int, d: int) -> int:
    """Chuyển đổi tọa độ (hàng r, cột c, chữ số d) thành chỉ số biến SAT (1-based: 1..729)."""
    return 81 * r + 9 * c + d


def cell_variables(r: int, c: int) -> List[int]:
    """Các biến tương ứng với ô (r, c) có thể nhận giá trị từ 1 đến 9."""
    return [var(r, c, d) for d in range(1, 10)]


def row_variables(r: int, d: int) -> List[int]:
    """Các biến tương ứng với chữ số d xuất hiện trong hàng r."""
    return [var(r, c, d) for c in range(9)]


def column_variables(c: int, d: int) -> List[int]:
    """Các biến tương ứng với chữ số d xuất hiện trong cột c."""
    return [var(r, c, d) for r in range(9)]


def block_variables(br: int, bc: int, d: int) -> List[int]:
    """Các biến tương ứng với chữ số d xuất hiện trong khối 3x3 (br, bc)."""
    return [
        var(r, c, d)
        for r in range(br * 3, br * 3 + 3)
        for c in range(bc * 3, bc * 3 + 3)
    ]


def encode_sudoku(grid: List[List[int]], method: str = "pairwise") -> Tuple[List[List[int]], int]:
    """
    Mã hóa toàn bộ bài toán Sudoku sang dạng CNF (Conjunctive Normal Form).

    Tham số:
        grid: Ma trận 9x9 với các số từ 0 (ô trống) đến 9.
        method: Phương pháp mã hóa AMO ('pairwise', 'binary', 'commander', 'product', 'seqcounter').

    Trả về:
        (clauses, top_id): Danh sách mệnh đề CNF và ID biến lớn nhất.
    """
    clauses: List[List[int]] = []
    top_id = 729  # 81 ô x 9 chữ số = 729 biến ban đầu

    # 1. Mỗi hàng chứa mỗi chữ số đúng 1 lần
    for r in range(9):
        for d in range(1, 10):
            cls, top_id = exactly_one(row_variables(r, d), method=method, top_id=top_id)
            clauses.extend(cls)

    # 2. Mỗi cột chứa mỗi chữ số đúng 1 lần
    for c in range(9):
        for d in range(1, 10):
            cls, top_id = exactly_one(column_variables(c, d), method=method, top_id=top_id)
            clauses.extend(cls)

    # 3. Mỗi khối 3x3 chứa mỗi chữ số đúng 1 lần
    for br in range(3):
        for bc in range(3):
            for d in range(1, 10):
                cls, top_id = exactly_one(block_variables(br, bc, d), method=method, top_id=top_id)
                clauses.extend(cls)

    # 4. Mỗi ô chứa đúng 1 chữ số
    for r in range(9):
        for c in range(9):
            cls, top_id = exactly_one(cell_variables(r, c), method=method, top_id=top_id)
            clauses.extend(cls)

    # 5. Các gợi ý có sẵn từ đề bài (Clues)
    for r in range(9):
        for c in range(9):
            d = grid[r][c]
            if d != 0:
                clauses.append([var(r, c, d)])

    return clauses, top_id


def decode_model(model: Optional[List[int]]) -> Optional[List[List[int]]]:
    """
    Giải mã mô hình thỏa mãn (SAT model) thành bảng nghiệm Sudoku 9x9.
    Tự động bỏ qua các biến phụ sinh ra từ AMO (id > 729).
    """
    if not model:
        return None

    grid = [[0 for _ in range(9)] for _ in range(9)]
    for x in model:
        if 1 <= x <= 729:
            val = x - 1
            r = val // 81
            rem = val % 81
            c = rem // 9
            d = rem % 9 + 1
            grid[r][c] = d

    return grid


def solve_sudoku_sat(grid: List[List[int]], method: str = "pairwise") -> Optional[List[List[int]]]:
    """
    Giải Sudoku bằng SAT Solver (Glucose3).
    
    Tham số:
        grid: Ma trận Sudoku 9x9.
        method: Phương pháp mã hóa ('pairwise', 'binary', 'commander', 'product', 'seqcounter').
    """
    clauses, _ = encode_sudoku(grid, method=method)
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        return decode_model(model)
    return None


if __name__ == "__main__":
    for m in ["pairwise", "binary", "commander", "product", "seqcounter"]:
        print(f"\n--- Testing SAT method: {m.upper()} ---")
        sol = solve_sudoku_sat(DEFAULT_GRID, method=m)
        if sol:
            print_grid(sol, f"GIAI SUDOKU BANG SAT ({m})")
        else:
            print("Khong tim thay nghiem.")
