"""
Module plotter: Cung cấp các hàm trực quan hóa hiệu năng các phương pháp giải Sudoku
và các kỹ thuật mã hóa SAT AMO/ALO bằng Matplotlib.
Hỗ trợ:
- Vẽ biểu đồ cột so sánh thời gian Encode vs Solve của các phương pháp SAT Encodings.
- Vẽ biểu đồ so sánh số biến và số clauses sinh ra.
- Vẽ biểu đồ so sánh hiệu năng các Solver (SAT, CP-SAT, ILP,...).
- Phân tích hiệu năng theo cấp độ khó (Easy, Medium, Hard, Expert).
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import numpy as np


def ensure_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def plot_encodings_benchmark(
    stats: Dict[str, Dict[str, Any]],
    output_path: str = "reports/benchmark_encodings.png",
    title_suffix: str = ""
):
    """
    Vẽ biểu đồ so sánh 5 phương pháp SAT Encodings:
    1. Thời gian Encode vs Solve (ms)
    2. Số biến & số clauses sinh ra
    """
    out_file = ensure_dir(Path(output_path))

    methods = list(stats.keys())
    labels = [stats[m].get("label", m) for m in methods]

    avg_enc = [np.mean(stats[m]["t_enc"]) for m in methods]
    avg_solve = [np.mean(stats[m]["t_solve"]) for m in methods]
    avg_vars = [np.mean(stats[m]["vars"]) for m in methods]
    avg_clauses = [np.mean(stats[m]["clauses"]) for m in methods]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Subplot 1: Thời gian Encode vs Solve (Stacked/Grouped Bar Chart)
    x = np.arange(len(methods))
    width = 0.35

    rects1 = ax1.bar(x - width / 2, avg_enc, width, label="Encode Time (ms)", color="#3498db")
    rects2 = ax1.bar(x + width / 2, avg_solve, width, label="Solve Time (ms)", color="#2ecc71")

    ax1.set_ylabel("Thời gian (ms)")
    ax1.set_title(f"Thời gian Encode và Solve trung bình {title_suffix}")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.7)

    # Thêm nhãn số liệu lên các cột
    for r in rects1:
        h = r.get_height()
        ax1.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    for r in rects2:
        h = r.get_height()
        ax1.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    # Subplot 2: Kích thước CNF (Số biến và số clauses)
    ax2_var = ax2
    ax2_clause = ax2.twinx()

    rects3 = ax2_var.bar(x - width / 2, avg_vars, width, label="Số biến phụ", color="#e67e22")
    rects4 = ax2_clause.bar(x + width / 2, avg_clauses, width, label="Số Clauses", color="#e74c3c")

    ax2_var.set_ylabel("Số biến", color="#e67e22")
    ax2_clause.set_ylabel("Số Clauses", color="#e74c3c")
    ax2_var.set_title(f"Quy mô mô hình CNF (Biến & Clauses) {title_suffix}")
    ax2_var.set_xticks(x)
    ax2_var.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax2_var.grid(axis="y", linestyle="--", alpha=0.7)

    # Gộp legend của twin axes
    lines1, labels1 = ax2_var.get_legend_handles_labels()
    lines2, labels2 = ax2_clause.get_legend_handles_labels()
    ax2_var.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"[Plotter] Đã xuất biểu đồ so sánh SAT Encodings: {out_file}")


def plot_solvers_benchmark(
    solver_stats: Dict[str, Dict[str, Any]],
    output_path: str = "reports/benchmark_solvers.png",
    title_suffix: str = ""
):
    """
    Vẽ biểu đồ cột so sánh thời gian thực thi giữa các Solvers (SAT, CP-SAT, ILP,...)
    kèm thanh độ lệch min/max hoặc standard deviation.
    """
    out_file = ensure_dir(Path(output_path))

    names = []
    avg_times = []
    min_times = []
    max_times = []

    for name, data in solver_stats.items():
        times = data.get("times", [])
        if times:
            names.append(name)
            avg_times.append(np.mean(times))
            min_times.append(np.min(times))
            max_times.append(np.max(times))

    if not names:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(names))

    # Dùng lỗi bất đối xứng [avg - min, max - avg]
    err_low = np.array(avg_times) - np.array(min_times)
    err_high = np.array(max_times) - np.array(avg_times)
    yerr = [err_low, err_high]

    colors = ["#2ecc71" if "SAT" in n else ("#3498db" if "CP" in n else "#e67e22") for n in names]

    bars = ax.barh(y_pos, avg_times, xerr=yerr, align="center", color=colors, alpha=0.85, capsize=4)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.invert_yaxis()  # Đưa solver nhanh nhất hoặc đầu tiên lên trên
    ax.set_xlabel("Thời gian giải trung bình (ms)")
    ax.set_title(f"So sánh thời gian giải giữa các Solver {title_suffix}")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    for bar, avg_t in zip(bars, avg_times):
        ax.text(avg_t + (max(avg_times) * 0.02), bar.get_y() + bar.get_height() / 2,
                f"{avg_t:.2f} ms", va="center", ha="left", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"[Plotter] Đã xuất biểu đồ so sánh Solvers: {out_file}")


def plot_difficulty_comparison(
    diff_data: Dict[str, Dict[str, float]],
    output_path: str = "reports/benchmark_difficulty.png",
    title: str = "Hiệu năng theo cấp độ khó Sudoku"
):
    """
    diff_data có cấu trúc:
    {
        "Method/Solver Name": {"easy": avg_ms, "medium": avg_ms, "hard": avg_ms, "expert": avg_ms}
    }
    """
    out_file = ensure_dir(Path(output_path))
    difficulties = ["easy", "medium", "hard", "expert"]
    diff_labels = ["Easy", "Medium", "Hard", "Expert"]

    fig, ax = plt.subplots(figsize=(11, 6))

    for method, diff_scores in diff_data.items():
        y_vals = [diff_scores.get(d, 0.0) for d in difficulties]
        ax.plot(diff_labels, y_vals, marker="o", linewidth=2, label=method)

    ax.set_xlabel("Cấp độ khó")
    ax.set_ylabel("Thời gian trung bình (ms)")
    ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"[Plotter] Đã xuất biểu đồ phân tích theo độ khó: {out_file}")
