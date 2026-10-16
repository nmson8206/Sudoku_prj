import sys
import math
from typing import List, Tuple

# Đảm bảo hiển thị tiếng Việt UTF-8 trên Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ma trận đề bài Sudoku 9x9 chuẩn dùng chung
DEFAULT_GRID = [
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

# Ma trận đề bài Sudoku 4x4 mẫu
DEFAULT_GRID_4X4 = [
    [1, 0, 3, 0],
    [0, 0, 0, 1],
    [4, 0, 0, 0],
    [0, 2, 0, 4]
]

# Ma trận đề bài Sudoku 16x16 mẫu (Hexadoku)
DEFAULT_GRID_16X16 = [
    [0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0],
    [0, 1, 0, 0,  0, 2, 0, 0,  0, 3, 0, 0,  0, 4, 0, 0],
    [0, 0, 5, 0,  0, 0, 6, 0,  0, 0, 7, 0,  0, 0, 8, 0],
    [0, 0, 0, 9,  0, 0, 0, 10, 0, 0, 0, 11, 0, 0, 0, 12],

    [0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0],
    [0, 13, 0, 0, 0, 14, 0, 0, 0, 15, 0, 0, 0, 16, 0, 0],
    [0, 0, 1, 0,  0, 0, 2, 0,  0, 0, 3, 0,  0, 0, 4, 0],
    [0, 0, 0, 5,  0, 0, 0, 6,  0, 0, 0, 7,  0, 0, 0, 8],

    [0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0],
    [0, 9, 0, 0,  0, 10, 0, 0, 0, 11, 0, 0, 0, 12, 0, 0],
    [0, 0, 13, 0, 0, 0, 14, 0, 0, 0, 15, 0, 0, 0, 16, 0],
    [0, 0, 0, 1,  0, 0, 0, 2,  0, 0, 0, 3,  0, 0, 0, 4],

    [0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0],
    [0, 5, 0, 0,  0, 6, 0, 0,  0, 7, 0, 0,  0, 8, 0, 0],
    [0, 0, 9, 0,  0, 0, 10, 0, 0, 0, 11, 0, 0, 0, 12, 0],
    [0, 0, 0, 13, 0, 0, 0, 14, 0, 0, 0, 15, 0, 0, 0, 16]
]


def get_grid_params(grid: List[List[int]]) -> Tuple[int, int, int]:
    """
    Xác định kích thước N và kích thước khối (block_r, block_c) của bảng Sudoku.
    Trả về: (N, block_r, block_c).
    """
    if not grid or not isinstance(grid, list):
        raise ValueError("Bảng Sudoku không hợp lệ: phải là một danh sách các hàng.")
    N = len(grid)
    for r, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != N:
            raise ValueError(f"Hàng {r} có kích thước {len(row)} không khớp với N = {N}.")

    # Kiểm tra kích thước khối
    isqrt_n = math.isqrt(N)
    if isqrt_n * isqrt_n == N:
        return N, isqrt_n, isqrt_n
    elif N == 6:
        return 6, 2, 3
    elif N == 12:
        return 12, 3, 4
    else:
        # Tìm ước số gần căn bậc hai nhất
        for r in range(isqrt_n, 0, -1):
            if N % r == 0:
                return N, r, N // r
        return N, 1, N


def print_grid(grid: List[List[int]], title: str = "KET QUA"):
    """In bảng Sudoku N x N dưới dạng kẻ khung trực quan."""
    N, br, bc = get_grid_params(grid)
    cell_w = max(2, len(str(N)))

    print(f"\n=== {title} ({N}x{N}) ===")
    
    # Tính độ dài đường ngang phân cách
    line_parts = []
    for _ in range(N // bc):
        line_parts.append("-" * (bc * (cell_w + 1) - 1))
    separator = "+".join(line_parts)

    for r in range(N):
        if r % br == 0 and r != 0:
            print(separator)
        row_str = []
        for c in range(N):
            if c % bc == 0 and c != 0:
                row_str.append("|")
            val = grid[r][c]
            val_str = str(val) if val != 0 else "."
            row_str.append(f"{val_str:>{cell_w}}")
        print(" ".join(row_str))
    print()
