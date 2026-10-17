"""
Unit tests kiểm tra module dataset_loader:
- Chuẩn hóa chuỗi 81 ký tự sang grid và ngược lại (string_to_grid, grid_to_string).
- Chuẩn hóa các định dạng dữ liệu thô (chuỗi, flat list, ma trận 2D).
- Xác định cấp độ khó (infer_difficulty).
- Tải và xử lý dataset chuẩn hóa từ cache và hub.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from benchmarks.dataset_loader import (
    string_to_grid,
    grid_to_string,
    infer_difficulty,
    normalize_puzzle,
    load_normalized_dataset,
    get_default_fallback_puzzles,
)
from solvers.sat_solver import solve_sudoku_sat
from tests.test_solvers import validate_sudoku_solution


def test_string_grid_conversion():
    test_str = (
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    )
    grid = string_to_grid(test_str)
    assert len(grid) == 9 and len(grid[0]) == 9, "Grid phải có kích thước 9x9"
    assert grid[0][0] == 5 and grid[0][1] == 3 and grid[0][2] == 0

    reconstructed = grid_to_string(grid)
    assert reconstructed == test_str, "Chuỗi sau khi tái tạo phải trùng khớp chuỗi gốc"

    # Kiểm tra chuyển đổi dấu chấm '.' thành '0'
    dot_str = test_str.replace("0", ".")
    grid_from_dots = string_to_grid(dot_str)
    assert grid_from_dots == grid, "Dấu '.' phải được chuẩn hóa thành 0"
    print("[PASSED] test_string_grid_conversion")


def test_infer_difficulty():
    assert infer_difficulty(17) == "expert"
    assert infer_difficulty(21) == "expert"
    assert infer_difficulty(25) == "hard"
    assert infer_difficulty(30) == "medium"
    assert infer_difficulty(40) == "easy"

    assert infer_difficulty(30, explicit_label="Diabolical") == "expert"
    assert infer_difficulty(30, explicit_label="Hard") == "hard"
    assert infer_difficulty(20, explicit_label="Easy") == "easy"
    print("[PASSED] test_infer_difficulty")


def test_normalize_puzzle_formats():
    # 1. Định dạng chuỗi 81 ký tự
    raw_s = "0" * 81
    p1 = normalize_puzzle(raw_s, "test_1", "test_source", "test_ds")
    assert p1["id"] == "test_1"
    assert p1["clues_count"] == 0
    assert p1["difficulty"] == "expert"
    assert len(p1["grid"]) == 9

    # 2. Định dạng ma trận 2D
    raw_2d = [[0] * 9 for _ in range(9)]
    raw_2d[0][0] = 5
    raw_2d[1][1] = 9
    p2 = normalize_puzzle(raw_2d, "test_2", "kagglehub", "top95")
    assert p2["clues_count"] == 2
    assert p2["source"] == "kagglehub"
    assert p2["puzzle_string"].startswith("50000000009")

    # 3. Định dạng flat list 81 phần tử
    raw_flat = [0] * 81
    raw_flat[0] = 7
    p3 = normalize_puzzle(raw_flat, "test_3", "huggingface", "ritvik")
    assert p3["clues_count"] == 1
    assert p3["grid"][0][0] == 7
    print("[PASSED] test_normalize_puzzle_formats")


def test_fallback_dataset():
    puzzles = get_default_fallback_puzzles()
    assert len(puzzles) >= 5, "Fallback dataset phải có ít nhất 5 puzzles"
    for p in puzzles:
        assert "grid" in p and len(p["grid"]) == 9
        assert "puzzle_string" in p and len(p["puzzle_string"]) == 81
        assert p["source"] in ["kagglehub", "huggingface"]
        # Thử giải bằng SAT Product
        sol = solve_sudoku_sat(p["grid"], method="product")
        assert sol is not None, f"Solver không giải được puzzle fallback {p['id']}"
        assert validate_sudoku_solution(sol, initial_grid=p["grid"])
    print("[PASSED] test_fallback_dataset (tất cả puzzle fallback giải thành công)")


def test_load_normalized_dataset():
    puzzles = load_normalized_dataset(limit=4)
    assert len(puzzles) <= 4
    for p in puzzles:
        assert isinstance(p["grid"], list) and len(p["grid"]) == 9
        assert p["difficulty"] in ["easy", "medium", "hard", "expert"]
    print("[PASSED] test_load_normalized_dataset")


def run_all():
    print("=" * 64)
    print("TEST SUITE: DATASET LOADER & NORMALIZATION")
    print("=" * 64)
    test_string_grid_conversion()
    test_infer_difficulty()
    test_normalize_puzzle_formats()
    test_fallback_dataset()
    test_load_normalized_dataset()
    print("=" * 64)
    print("TẤT CẢ TESTS CHO DATASET VÀ CHUẨN HÓA DỮ LIỆU ĐỀU ĐẠT!")


if __name__ == "__main__":
    run_all()
