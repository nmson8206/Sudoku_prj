import sys

# Đảm bảo hiển thị tiếng Việt UTF-8 trên Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ma trận đề bài Sudoku chuẩn dùng chung
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


def print_grid(grid, title="KET QUA"):
    """In bảng Sudoku dưới dạng kẻ khung trực quan."""
    print(f"\n=== {title} ===")
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        row_str = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str.append("|")
            val = grid[r][c]
            row_str.append(str(val) if val != 0 else ".")
        print(" ".join(row_str))
    print()
