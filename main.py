"""
Điểm khởi chạy chính (CLI Entry Point) của dự án Sudoku Solver & SAT Encodings.
Hỗ trợ giải các kích thước N x N (4x4, 9x9, 16x16,...).
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import argparse
from utils import DEFAULT_GRID, DEFAULT_GRID_4X4, DEFAULT_GRID_16X16, print_grid
from solvers import solve_sudoku_sat
from benchmarks import benchmark_solvers, benchmark_encodings
from tests.test_encodings import run_all as run_encoding_tests
from tests.test_solvers import run_all as run_solver_tests


def main():
    parser = argparse.ArgumentParser(
        description="Sudoku Solver & SAT Cardinality Encodings (Hỗ trợ kích thước NxN tổng quát)"
    )
    parser.add_argument(
        "--solve",
        choices=["pairwise", "binary", "commander", "product", "seqcounter"],
        default="product",
        help="Giải Sudoku bằng SAT với phương pháp encoding được chọn (mặc định: product)"
    )
    parser.add_argument(
        "--size",
        choices=["4", "9", "16"],
        default="9",
        help="Kích thước Sudoku mẫu (4, 9, hoặc 16, mặc định: 9)"
    )
    parser.add_argument(
        "--benchmark-all",
        action="store_true",
        help="Chạy benchmark so sánh tất cả các solver (SAT, CP-SAT, ILP, Gurobi, CPLEX)"
    )
    parser.add_argument(
        "--benchmark-sat",
        action="store_true",
        help="Chạy benchmark so sánh 5 phương pháp mã hóa SAT AMO/ALO"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Chạy toàn bộ unit tests và integration tests"
    )

    args = parser.parse_args()

    if args.test:
        run_encoding_tests()
        print()
        run_solver_tests()
    elif args.benchmark_all:
        grid = DEFAULT_GRID_16X16 if args.size == "16" else (DEFAULT_GRID_4X4 if args.size == "4" else DEFAULT_GRID)
        benchmark_solvers(grid=grid)
    elif args.benchmark_sat:
        grid = DEFAULT_GRID_16X16 if args.size == "16" else (DEFAULT_GRID_4X4 if args.size == "4" else DEFAULT_GRID)
        benchmark_encodings(grid=grid)
    else:
        # Chọn grid theo kích thước
        if args.size == "4":
            grid = DEFAULT_GRID_4X4
        elif args.size == "16":
            grid = DEFAULT_GRID_16X16
        else:
            grid = DEFAULT_GRID

        N = len(grid)
        print(f"--- ĐANG GIẢI SUDOKU {N}x{N} BẰNG SAT ({args.solve.upper()}) ---")
        sol = solve_sudoku_sat(grid, method=args.solve)
        if sol:
            print_grid(sol, f"KẾT QUẢ GIẢI SUDOKU BẰNG SAT ({args.solve})")
        else:
            print("Không tìm thấy nghiệm.")


if __name__ == "__main__":
    main()
