"""
Script benchmark so sánh hiệu năng các Solver và các SAT Cardinality Encodings
trên tập dữ liệu chuẩn hóa (Dataset) được thu thập từ KaggleHub và Hugging Face.

Đo lường chi tiết:
- Số biến, số clauses, thời gian encode và solve của 5 phương pháp SAT Encodings.
- Thời gian giải, tỷ lệ thành công của các solver (SAT, CP-SAT, ILP, Gurobi, CPLEX).
- Phân tích hiệu năng theo cấp độ khó (Easy, Medium, Hard, Expert) và nguồn dữ liệu (KaggleHub, Hugging Face).
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import time
import argparse
from typing import List, Dict, Any, Optional
from pysat.solvers import Glucose3

from benchmarks.dataset_loader import (
    load_normalized_dataset,
    prepare_benchmark_dataset,
    string_to_grid,
    DEFAULT_DATASET_PATH,
)
from solvers.sat_solver import encode_sudoku, decode_model, solve_sudoku_sat
from solvers import (
    solve_sudoku_cpsat,
    solve_sudoku_ilp,
    solve_sudoku_cplex_cp,
    solve_sudoku_gurobi,
    solve_sudoku_cplex_mip,
)
from tests.test_solvers import validate_sudoku_solution


def benchmark_dataset_encodings(
    puzzles: Optional[List[Dict[str, Any]]] = None,
    source: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: Optional[int] = None,
    plot: bool = False,
    output_csv: Optional[str] = None,
    output_json: Optional[str] = None,
    plot_path: str = "reports/benchmark_encodings.png",
):
    """
    Benchmark so sánh 5 kỹ thuật mã hóa SAT Cardinality (AMO/ALO) trên tập dữ liệu chuẩn hóa.
    Hỗ trợ xuất CSV, JSON và tự động vẽ biểu đồ Matplotlib.
    """
    if puzzles is None:
        puzzles = load_normalized_dataset(source=source, difficulty=difficulty, limit=limit)

    if not puzzles:
        print("[LỖI] Không có dữ liệu Sudoku nào để chạy benchmark encodings.")
        return

    methods = [
        ("Pairwise (Naive)", "pairwise"),
        ("Binary (PySAT Bitwise)", "binary"),
        ("Commander Encoding", "commander"),
        ("Product Encoding (Chen)", "product"),
        ("Sequential Counter (PySAT)", "seqcounter"),
    ]

    total_puzzles = len(puzzles)
    print("=" * 95)
    print(f"BENCHMARK SAT ENCODINGS TRÊN DATASET ({total_puzzles} PUZZLES TỪ NORVIG, KAGGLEHUB & HUGGING FACE)")
    print("=" * 95)
    print(f"{'PHƯƠNG PHÁP':<27} | {'SỐ BIẾN TB':<10} | {'SỐ CLAUSES':<11} | {'ENCODE(ms)':<11} | {'SOLVE(ms)':<10} | {'TỔNG(ms)':<10} | {'VALID':<6}")
    print("=" * 95)

    stats: Dict[str, Dict[str, Any]] = {
        key: {
            "label": label,
            "vars": [],
            "clauses": [],
            "t_enc": [],
            "t_solve": [],
            "t_total": [],
            "success": 0,
        }
        for label, key in methods
    }

    records: List[Dict[str, Any]] = []

    # Chạy đo lường trên từng puzzle
    for idx_p, p in enumerate(puzzles):
        grid = p["grid"]
        N = len(grid)
        p_id = p.get("id", f"puzzle_{idx_p + 1}")
        diff = p.get("difficulty", "unknown")

        for label, key in methods:
            t0 = time.perf_counter()
            clauses, top_id = encode_sudoku(grid, method=key)
            t_enc_ms = (time.perf_counter() - t0) * 1000

            solver = Glucose3()
            for cl in clauses:
                solver.add_clause(cl)

            t1 = time.perf_counter()
            solved = solver.solve()
            t_solve_ms = (time.perf_counter() - t1) * 1000

            model = solver.get_model() if solved else None
            res = decode_model(model, N=N)
            is_valid = validate_sudoku_solution(res, initial_grid=grid)

            t_total_ms = t_enc_ms + t_solve_ms
            stats[key]["vars"].append(top_id)
            stats[key]["clauses"].append(len(clauses))
            stats[key]["t_enc"].append(t_enc_ms)
            stats[key]["t_solve"].append(t_solve_ms)
            stats[key]["t_total"].append(t_total_ms)
            if is_valid:
                stats[key]["success"] += 1

            records.append({
                "puzzle_id": p_id,
                "difficulty": diff,
                "method_key": key,
                "method_name": label,
                "num_vars": top_id,
                "num_clauses": len(clauses),
                "encode_ms": round(t_enc_ms, 3),
                "solve_ms": round(t_solve_ms, 3),
                "total_ms": round(t_total_ms, 3),
                "is_valid": is_valid,
            })

    # In kết quả tổng hợp
    summary_data = {}
    for label, key in methods:
        st = stats[key]
        avg_vars = sum(st["vars"]) / total_puzzles
        avg_clauses = sum(st["clauses"]) / total_puzzles
        avg_enc = sum(st["t_enc"]) / total_puzzles
        avg_solve = sum(st["t_solve"]) / total_puzzles
        avg_total = sum(st["t_total"]) / total_puzzles
        valid_str = f"{st['success']}/{total_puzzles}"

        summary_data[key] = {
            "name": label,
            "avg_vars": avg_vars,
            "avg_clauses": avg_clauses,
            "avg_encode_ms": avg_enc,
            "avg_solve_ms": avg_solve,
            "avg_total_ms": avg_total,
            "valid_ratio": valid_str,
        }

        print(
            f"{label:<27} | {avg_vars:>10.0f} | {avg_clauses:>11.0f} | {avg_enc:>9.2f} ms | {avg_solve:>8.2f} ms | {avg_total:>8.2f} ms | {valid_str:>6}"
        )
    print("=" * 95)

    # Phân tích theo cấp độ khó
    difficulties = ["easy", "medium", "hard", "expert"]
    diff_puzzles = {d: [p for p in puzzles if p["difficulty"] == d] for d in difficulties}
    present_diffs = [d for d in difficulties if len(diff_puzzles[d]) > 0]
    diff_chart_data: Dict[str, Dict[str, float]] = {}

    if len(present_diffs) > 1:
        print("\nPHÂN TÍCH THỜI GIAN GIẢI SAT (TỔNG MS) THEO ĐỘ KHÓ:")
        print("-" * 75)
        diff_labels = [f"{d.upper()} ({len(diff_puzzles[d])})" for d in present_diffs]
        header_diff = f"{'PHƯƠNG PHÁP':<27} | " + " | ".join(f"{lbl:>12}" for lbl in diff_labels)
        print(header_diff)
        print("-" * 75)

        for label, key in methods:
            cols = []
            diff_chart_data[label] = {}
            for d in present_diffs:
                subset = diff_puzzles[d]
                sub_indices = [i for i, p in enumerate(puzzles) if p["difficulty"] == d]
                sub_times = [stats[key]["t_total"][i] for i in sub_indices]
                avg_t = sum(sub_times) / len(sub_times) if sub_times else 0
                cols.append(f"{avg_t:>9.2f} ms")
                diff_chart_data[label][d] = round(avg_t, 2)
            print(f"{label:<27} | " + " | ".join(cols))
        print("-" * 75)
    print()

    # Xuất ra file CSV nếu được yêu cầu
    if output_csv:
        import pandas as pd
        from pathlib import Path
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(records).to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"[Export] Đã lưu dữ liệu chi tiết SAT Encodings ra: {output_csv}")

    # Xuất ra file JSON nếu được yêu cầu
    if output_json:
        import json
        from pathlib import Path
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump({"summary": summary_data, "details": records}, f, indent=2, ensure_ascii=False)
        print(f"[Export] Đã lưu tóm tắt JSON ra: {output_json}")

    # Vẽ biểu đồ Matplotlib nếu được yêu cầu
    if plot:
        from benchmarks.plotter import plot_encodings_benchmark, plot_difficulty_comparison
        plot_encodings_benchmark(stats, output_path=plot_path, title_suffix=f"({total_puzzles} puzzles)")
        if diff_chart_data:
            diff_plot_path = str(Path(plot_path).parent / "benchmark_encodings_difficulty.png")
            plot_difficulty_comparison(diff_chart_data, output_path=diff_plot_path, title=f"Thời gian SAT Encodings theo độ khó ({total_puzzles} puzzles)")



def benchmark_dataset_solvers(
    puzzles: Optional[List[Dict[str, Any]]] = None,
    source: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: Optional[int] = None,
    plot: bool = False,
    output_csv: Optional[str] = None,
    output_json: Optional[str] = None,
    plot_path: str = "reports/benchmark_solvers.png",
):
    """
    Benchmark so sánh tất cả các Solver trên tập dữ liệu chuẩn hóa.
    Hỗ trợ xuất CSV, JSON và tự động vẽ biểu đồ Matplotlib.
    """
    if puzzles is None:
        puzzles = load_normalized_dataset(source=source, difficulty=difficulty, limit=limit)

    if not puzzles:
        print("[LỖI] Không có dữ liệu Sudoku nào để chạy benchmark solvers.")
        return

    solvers = [
        ("SAT (Glucose3 - Product)", lambda g: solve_sudoku_sat(g, method="product")),
        ("SAT (Glucose3 - Pairwise)", lambda g: solve_sudoku_sat(g, method="pairwise")),
        ("CP-SAT (Google OR-Tools)", solve_sudoku_cpsat),
        ("ILP (PuLP / CBC)", solve_sudoku_ilp),
        ("Gurobi (MIP)", solve_sudoku_gurobi),
        ("CPLEX CP (IBM CPO)", solve_sudoku_cplex_cp),
        ("CPLEX MIP (IBM MP)", solve_sudoku_cplex_mip),
    ]

    total_puzzles = len(puzzles)
    print("=" * 86)
    print(f"BENCHMARK CÁC SOLVER TRÊN DATASET ({total_puzzles} PUZZLES TỪ NORVIG, KAGGLEHUB & HUGGING FACE)")
    print("=" * 86)
    print(f"{'SOLVER':<30} | {'TỶ LỆ ĐÚNG':<12} | {'TB (ms)':<11} | {'MIN (ms)':<10} | {'MAX (ms)':<10}")
    print("=" * 86)

    solver_stats: Dict[str, Dict[str, Any]] = {
        name: {"times": [], "success": 0, "errors": 0} for name, _ in solvers
    }

    records: List[Dict[str, Any]] = []

    # Đo từng puzzle
    for idx_p, p in enumerate(puzzles):
        grid = p["grid"]
        p_id = p.get("id", f"puzzle_{idx_p + 1}")
        diff = p.get("difficulty", "unknown")

        for name, solver_fn in solvers:
            try:
                t0 = time.perf_counter()
                res = solver_fn(grid)
                elapsed_ms = (time.perf_counter() - t0) * 1000

                is_valid = bool(res and validate_sudoku_solution(res, initial_grid=grid))
                if is_valid:
                    solver_stats[name]["success"] += 1
                solver_stats[name]["times"].append(elapsed_ms)

                records.append({
                    "puzzle_id": p_id,
                    "difficulty": diff,
                    "solver_name": name,
                    "time_ms": round(elapsed_ms, 3),
                    "is_valid": is_valid,
                })
            except Exception as e:
                solver_stats[name]["errors"] += 1
                records.append({
                    "puzzle_id": p_id,
                    "difficulty": diff,
                    "solver_name": name,
                    "time_ms": None,
                    "is_valid": False,
                    "error": str(e),
                })

    summary_data = {}
    for name, _ in solvers:
        st = solver_stats[name]
        times = st["times"]
        success_ratio = f"{st['success']}/{total_puzzles}"
        if times:
            avg_ms = sum(times) / len(times)
            min_ms = min(times)
            max_ms = max(times)
            summary_data[name] = {
                "avg_ms": avg_ms,
                "min_ms": min_ms,
                "max_ms": max_ms,
                "success_ratio": success_ratio,
            }
            print(f"{name:<30} | {success_ratio:>12} | {avg_ms:>8.2f} ms | {min_ms:>7.2f} ms | {max_ms:>7.2f} ms")
        else:
            print(f"{name:<30} | {success_ratio:>12} | {'N/A':>10} | {'N/A':>9} | {'N/A':>9}")

    print("=" * 86)

    # Thống kê nhanh theo nguồn dataset
    kaggle_puzzles = [p for p in puzzles if p.get("source") in ["kagglehub", "norvig"]]
    hf_puzzles = [p for p in puzzles if p.get("source") == "huggingface"]

    if kaggle_puzzles and hf_puzzles:
        print("\nSO SÁNH THỜI GIAN TRUNG BÌNH THEO NGUỒN DATASET:")
        print("-" * 65)
        print(f"{'SOLVER':<30} | {'KAGGLE/NORVIG(ms)':<18} | {'HUGGING FACE (ms)':<15}")
        print("-" * 65)

        for name, solver_fn in solvers:
            # Đo Kaggle subset
            k_times = [r["time_ms"] for r in records if r["solver_name"] == name and r["puzzle_id"].startswith(("kaggle", "norvig")) and r["time_ms"] is not None]
            hf_times = [r["time_ms"] for r in records if r["solver_name"] == name and r["puzzle_id"].startswith("hf") and r["time_ms"] is not None]

            k_avg = f"{sum(k_times)/len(k_times):>15.2f} ms" if k_times else "              N/A"
            hf_avg = f"{sum(hf_times)/len(hf_times):>12.2f} ms" if hf_times else "         N/A"
            print(f"{name:<30} | {k_avg:<18} | {hf_avg:<15}")
        print("-" * 65)
    print()

    # Xuất ra file CSV nếu được yêu cầu
    if output_csv:
        import pandas as pd
        from pathlib import Path
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(records).to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"[Export] Đã lưu dữ liệu chi tiết Solvers ra: {output_csv}")

    # Xuất ra file JSON nếu được yêu cầu
    if output_json:
        import json
        from pathlib import Path
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump({"summary": summary_data, "details": records}, f, indent=2, ensure_ascii=False)
        print(f"[Export] Đã lưu tóm tắt Solvers JSON ra: {output_json}")

    # Vẽ biểu đồ Matplotlib nếu được yêu cầu
    if plot:
        from benchmarks.plotter import plot_solvers_benchmark
        plot_solvers_benchmark(solver_stats, output_path=plot_path, title_suffix=f"({total_puzzles} puzzles)")



def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Sudoku Solvers & SAT Encodings trên Dataset từ KaggleHub & Hugging Face"
    )
    parser.add_argument(
        "--encodings",
        action="store_true",
        help="Chạy benchmark so sánh 5 kỹ thuật mã hóa SAT AMO/ALO"
    )
    parser.add_argument(
        "--solvers",
        action="store_true",
        help="Chạy benchmark so sánh các Solver (SAT, CP-SAT, ILP, Gurobi, CPLEX)"
    )
    parser.add_argument(
        "--source",
        choices=["all", "kaggle", "huggingface"],
        default="all",
        help="Lọc nguồn dataset (all, kaggle, huggingface, mặc định: all)"
    )
    parser.add_argument(
        "--difficulty",
        choices=["all", "easy", "medium", "hard", "expert"],
        default="all",
        help="Lọc độ khó (all, easy, medium, hard, expert, mặc định: all)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Số lượng puzzle tối đa cần benchmark (mặc định: toàn bộ)"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ép tải và chuẩn hóa lại dataset từ KaggleHub và Hugging Face"
    )

    args = parser.parse_args()

    if args.refresh:
        prepare_benchmark_dataset(force_download=True)

    # Nếu không chỉ định cụ thể, chạy cả hai
    run_enc = args.encodings or (not args.encodings and not args.solvers)
    run_solv = args.solvers or (not args.encodings and not args.solvers)

    puzzles = load_normalized_dataset(
        source=args.source if args.source != "all" else None,
        difficulty=args.difficulty if args.difficulty != "all" else None,
        limit=args.limit,
    )

    if run_enc:
        benchmark_dataset_encodings(puzzles=puzzles)
    if run_solv:
        benchmark_dataset_solvers(puzzles=puzzles)


if __name__ == "__main__":
    main()
