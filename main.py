"""
Điểm khởi chạy chính (CLI Entry Point) của dự án Sudoku Solver & SAT Encodings.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import argparse
from utils import DEFAULT_GRID, print_grid
from solvers import solve_sudoku_sat
from benchmarks import benchmark_solvers, benchmark_encodings
from tests.test_encodings import run_all as run_encoding_tests
from tests.test_solvers import run_all as run_solver_tests


def main():
    parser = argparse.ArgumentParser(
        description="Sudoku Solver & SAT Cardinality Encodings (AMO / ALO Benchmark Framework)"
    )
    parser.add_argument(
        "--solve",
        choices=["pairwise", "binary", "commander", "product", "seqcounter"],
        default="product",
        help="Giải Sudoku bằng SAT với phương pháp encoding được chọn (mặc định: product)"
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
        benchmark_solvers()
    elif args.benchmark_sat:
        benchmark_encodings()
    else:
        # Chạy demo giải Sudoku bằng SAT
        print(f"--- ĐANG GIẢI SUDOKU BẰNG SAT ({args.solve.upper()}) ---")
        sol = solve_sudoku_sat(DEFAULT_GRID, method=args.solve)
        if sol:
            print_grid(sol, f"KẾT QUẢ GIẢI SUDOKU BẰNG SAT ({args.solve})")
        else:
            print("Không tìm thấy nghiệm.")


if __name__ == "__main__":
    main()
