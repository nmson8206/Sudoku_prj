"""
Điểm khởi chạy chính (CLI Entry Point) của dự án Sudoku Solver & SAT Encodings.
Hỗ trợ:
- Giải Sudoku các kích thước N x N (4x4, 9x9, 16x16,...).
- Benchmark Solver và SAT Encodings trên ma trận mẫu hoặc tập Dataset chuẩn hóa từ KaggleHub & Hugging Face.
- Chạy toàn bộ hệ thống Unit Tests và Integration Tests.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import argparse
from utils import DEFAULT_GRID, DEFAULT_GRID_4X4, DEFAULT_GRID_16X16, print_grid
from solvers import solve_sudoku_sat
from benchmarks import (
    benchmark_solvers,
    benchmark_encodings,
    benchmark_dataset_solvers,
    benchmark_dataset_encodings,
    prepare_benchmark_dataset,
    load_normalized_dataset,
)
from tests.test_encodings import run_all as run_encoding_tests
from tests.test_solvers import run_all as run_solver_tests
from tests.test_dataset import run_all as run_dataset_tests


def main():
    parser = argparse.ArgumentParser(
        description="Sudoku Solver, SAT Cardinality Encodings & Benchmarks (NxN & Kaggle/HuggingFace Datasets)"
    )
    # Nhóm tham số giải Sudoku đơn lẻ
    parser.add_argument(
        "--solve",
        choices=["pairwise", "binary", "commander", "product", "seqcounter"],
        default=None,
        help="Giải Sudoku bằng SAT với phương pháp encoding được chọn (pairwise, binary, commander, product, seqcounter)"
    )
    parser.add_argument(
        "--size",
        choices=["4", "9", "16"],
        default="9",
        help="Kích thước Sudoku mẫu (4, 9, hoặc 16, mặc định: 9)"
    )

    # Nhóm tham số benchmark truyền thống
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

    # Nhóm tham số benchmark trên Dataset (KaggleHub & Hugging Face)
    parser.add_argument(
        "--benchmark-dataset",
        action="store_true",
        help="Chạy toàn bộ benchmark (cả Solvers và SAT Encodings) trên Dataset từ KaggleHub & Hugging Face"
    )
    parser.add_argument(
        "--benchmark-dataset-solvers",
        action="store_true",
        help="Chạy benchmark so sánh các Solver trên Dataset từ KaggleHub & Hugging Face"
    )
    parser.add_argument(
        "--benchmark-dataset-encodings",
        action="store_true",
        help="Chạy benchmark so sánh 5 phương pháp SAT Encoding trên Dataset từ KaggleHub & Hugging Face"
    )
    parser.add_argument(
        "--prepare-data",
        action="store_true",
        help="Tải và chuẩn hóa dataset mới từ KaggleHub & Hugging Face và lưu vào data/benchmark_dataset.json"
    )
    parser.add_argument(
        "--source",
        choices=["all", "kaggle", "huggingface", "norvig"],
        default="all",
        help="Lọc nguồn dataset khi chạy benchmark (all, kaggle, huggingface, norvig, mặc định: all)"
    )
    parser.add_argument(
        "--difficulty",
        choices=["all", "easy", "medium", "hard", "expert"],
        default="all",
        help="Lọc cấp độ khó của dataset khi chạy benchmark (all, easy, medium, hard, expert, mặc định: all)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Giới hạn số lượng puzzle từ dataset để chạy benchmark"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Tự động vẽ và lưu biểu đồ so sánh hiệu năng vào thư mục reports/"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=None,
        help="Đường dẫn file CSV để lưu kết quả chi tiết từng bài test (ví dụ: reports/results.csv)"
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Đường dẫn file JSON để lưu tóm tắt thống kê benchmark"
    )

    # Kiểm thử
    parser.add_argument(
        "--test",
        action="store_true",
        help="Chạy toàn bộ unit tests, integration tests và dataset tests"
    )

    args = parser.parse_args()

    if args.prepare_data:
        prepare_benchmark_dataset(force_download=True)
    elif args.test:
        run_encoding_tests()
        print()
        run_solver_tests()
        print()
        run_dataset_tests()
    elif args.benchmark_dataset:
        puzzles = load_normalized_dataset(
            source=args.source if args.source != "all" else None,
            difficulty=args.difficulty if args.difficulty != "all" else None,
            limit=args.limit,
        )
        csv_enc = args.output_csv if args.output_csv else None
        csv_solv = args.output_csv.replace(".csv", "_solvers.csv") if args.output_csv else None
        benchmark_dataset_encodings(
            puzzles=puzzles,
            plot=args.plot,
            output_csv=csv_enc,
            output_json=args.output_json,
        )
        benchmark_dataset_solvers(
            puzzles=puzzles,
            plot=args.plot,
            output_csv=csv_solv,
            output_json=args.output_json.replace(".json", "_solvers.json") if args.output_json else None,
        )
    elif args.benchmark_dataset_solvers:
        puzzles = load_normalized_dataset(
            source=args.source if args.source != "all" else None,
            difficulty=args.difficulty if args.difficulty != "all" else None,
            limit=args.limit,
        )
        benchmark_dataset_solvers(
            puzzles=puzzles,
            plot=args.plot,
            output_csv=args.output_csv,
            output_json=args.output_json,
        )
    elif args.benchmark_dataset_encodings:
        puzzles = load_normalized_dataset(
            source=args.source if args.source != "all" else None,
            difficulty=args.difficulty if args.difficulty != "all" else None,
            limit=args.limit,
        )
        benchmark_dataset_encodings(
            puzzles=puzzles,
            plot=args.plot,
            output_csv=args.output_csv,
            output_json=args.output_json,
        )
    elif args.benchmark_all:
        grid = DEFAULT_GRID_16X16 if args.size == "16" else (DEFAULT_GRID_4X4 if args.size == "4" else DEFAULT_GRID)
        benchmark_solvers(grid=grid)
    elif args.benchmark_sat:
        grid = DEFAULT_GRID_16X16 if args.size == "16" else (DEFAULT_GRID_4X4 if args.size == "4" else DEFAULT_GRID)
        benchmark_encodings(grid=grid)
    elif args.solve:
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
    else:
        # Mặc định: giải ma trận 9x9 với Product encoding
        grid = DEFAULT_GRID
        print("--- ĐANG GIẢI SUDOKU 9x9 MẪU BẰNG SAT (PRODUCT) ---")
        sol = solve_sudoku_sat(grid, method="product")
        if sol:
            print_grid(sol, "KẾT QUẢ GIẢI SUDOKU BẰNG SAT (product)")
        else:
            print("Không tìm thấy nghiệm.")


if __name__ == "__main__":
    main()
