"""
Sudoku Solver bằng SAT (sử dụng solver Glucose3 từ thư viện PySAT).
Hỗ trợ chuyển đổi linh hoạt giữa các phương pháp mã hóa cardinality (AMO):
- 'pairwise'
- 'binary'
- 'commander'
- 'product'
- 'seqcounter'
Hỗ trợ giải Sudoku kích thước tổng quát N x N.
"""

from typing import Optional, List, Tuple
from pysat.solvers import Glucose3
from utils import DEFAULT_GRID, print_grid, get_grid_params
from sat_encodings import exactly_one


def var(r: int, c: int, d: int, N: int = 9) -> int:
    """Chuyển đổi tọa độ (hàng r, cột c, chữ số d) thành chỉ số biến SAT (1-based: 1..N^3)."""
    return N * N * r + N * c + d


def cell_variables(r: int, c: int, N: int = 9) -> List[int]:
    """Các biến tương ứng với ô (r, c) có thể nhận giá trị từ 1 đến N."""
    return [var(r, c, d, N) for d in range(1, N + 1)]


def row_variables(r: int, d: int, N: int = 9) -> List[int]:
    """Các biến tương ứng với chữ số d xuất hiện trong hàng r."""
    return [var(r, c, d, N) for c in range(N)]


def column_variables(c: int, d: int, N: int = 9) -> List[int]:
    """Các biến tương ứng với chữ số d xuất hiện trong cột c."""
    return [var(r, c, d, N) for r in range(N)]


def block_variables(br: int, bc: int, d: int, block_r: int = 3, block_c: int = 3, N: int = 9) -> List[int]:
    """Các biến tương ứng với chữ số d xuất hiện trong khối (br, bc)."""
    return [
        var(r, c, d, N)
        for r in range(br * block_r, (br + 1) * block_r)
        for c in range(bc * block_c, (bc + 1) * block_c)
    ]


def encode_sudoku(grid: List[List[int]], method: str = "pairwise") -> Tuple[List[List[int]], int]:
    """
    Mã hóa toàn bộ bài toán Sudoku N x N sang dạng CNF (Conjunctive Normal Form).

    Tham số:
        grid: Ma trận N x N với các số từ 0 (ô trống) đến N.
        method: Phương pháp mã hóa AMO ('pairwise', 'binary', 'commander', 'product', 'seqcounter').

    Trả về:
        (clauses, top_id): Danh sách mệnh đề CNF và ID biến lớn nhất.
    """
    N, block_r, block_c = get_grid_params(grid)
    clauses: List[List[int]] = []
    top_id = N * N * N  # N x N ô x N chữ số = N^3 biến ban đầu

    # 1. Mỗi hàng chứa mỗi chữ số đúng 1 lần
    for r in range(N):
        for d in range(1, N + 1):
            cls, top_id = exactly_one(row_variables(r, d, N), method=method, top_id=top_id)
            clauses.extend(cls)

    # 2. Mỗi cột chứa mỗi chữ số đúng 1 lần
    for c in range(N):
        for d in range(1, N + 1):
            cls, top_id = exactly_one(column_variables(c, d, N), method=method, top_id=top_id)
            clauses.extend(cls)

    # 3. Mỗi khối (block_r x block_c) chứa mỗi chữ số đúng 1 lần
    num_block_rows = N // block_r
    num_block_cols = N // block_c
    for br in range(num_block_rows):
        for bc in range(num_block_cols):
            for d in range(1, N + 1):
                cls, top_id = exactly_one(block_variables(br, bc, d, block_r, block_c, N), method=method, top_id=top_id)
                clauses.extend(cls)

    # 4. Mỗi ô chứa đúng 1 chữ số
    for r in range(N):
        for c in range(N):
            cls, top_id = exactly_one(cell_variables(r, c, N), method=method, top_id=top_id)
            clauses.extend(cls)

    # 5. Các gợi ý có sẵn từ đề bài (Clues)
    for r in range(N):
        for c in range(N):
            d = grid[r][c]
            if d != 0:
                clauses.append([var(r, c, d, N)])

    return clauses, top_id


def decode_model(model: Optional[List[int]], N: int = 9) -> Optional[List[List[int]]]:
    """
    Giải mã mô hình thỏa mãn (SAT model) thành bảng nghiệm Sudoku N x N.
    Tự động bỏ qua các biến phụ sinh ra từ AMO (id > N^3).
    """
    if not model:
        return None

    top_base = N * N * N
    grid = [[0 for _ in range(N)] for _ in range(N)]
    for x in model:
        if 1 <= x <= top_base:
            val = x - 1
            r = val // (N * N)
            rem = val % (N * N)
            c = rem // N
            d = rem % N + 1
            grid[r][c] = d

    return grid


def solve_sudoku_sat(grid: List[List[int]], method: str = "pairwise") -> Optional[List[List[int]]]:
    """
    Giải Sudoku N x N bằng SAT Solver (Glucose3).
    
    Tham số:
        grid: Ma trận Sudoku N x N.
        method: Phương pháp mã hóa ('pairwise', 'binary', 'commander', 'product', 'seqcounter').
    """
    N, _, _ = get_grid_params(grid)
    clauses, _ = encode_sudoku(grid, method=method)
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        return decode_model(model, N=N)
    return None


if __name__ == "__main__":
    for m in ["pairwise", "binary", "commander", "product", "seqcounter"]:
        print(f"\n--- Testing SAT method: {m.upper()} ---")
        sol = solve_sudoku_sat(DEFAULT_GRID, method=m)
        if sol:
            print_grid(sol, f"GIAI SUDOKU BANG SAT ({m})")
        else:
            print("Khong tim thay nghiem.")
