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
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            path.unlink()
        except Exception:
            pass
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

    rects3 = ax2_var.bar(x - width / 2, avg_vars, width, label="Số biến", color="#e67e22")
    rects4 = ax2_clause.bar(x + width / 2, avg_clauses, width, label="Số Clauses", color="#e74c3c")

    # Mở rộng giới hạn trục Y lên 25% để các cột cao nhất không bị đè bởi Legend
    max_v = max(avg_vars) if avg_vars else 1
    max_c = max(avg_clauses) if avg_clauses else 1
    ax2_var.set_ylim(0, max_v * 1.28)
    ax2_clause.set_ylim(0, max_c * 1.28)

    ax2_var.set_ylabel("Số biến", color="#e67e22", fontsize=10, fontweight="bold")
    ax2_clause.set_ylabel("Số Clauses", color="#e74c3c", fontsize=10, fontweight="bold")
    ax2_var.set_title(f"Quy mô mô hình CNF (Biến & Clauses) {title_suffix}", fontsize=11, fontweight="bold", pad=12)
    ax2_var.set_xticks(x)
    ax2_var.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax2_var.grid(axis="y", linestyle="--", alpha=0.7)

    # Thêm nhãn số liệu lên các cột
    for r in rects3:
        h = r.get_height()
        ax2_var.annotate(f"{int(h)}", xy=(r.get_x() + r.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#d35400")
    for r in rects4:
        h = r.get_height()
        ax2_clause.annotate(f"{int(h)}", xy=(r.get_x() + r.get_width() / 2, h),
                            xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#c0392b")

    # Gộp legend của twin axes, đặt nền bán trong suốt mờ bo tròn
    lines1, labels1 = ax2_var.get_legend_handles_labels()
    lines2, labels2 = ax2_clause.get_legend_handles_labels()
    ax2_var.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.9, fancybox=True)

    # Cũng mở rộng trục Y cho Subplot 1 để legend không bao giờ đè cột
    max_e = max(max(avg_enc) if avg_enc else 1, max(avg_solve) if avg_solve else 1)
    ax1.set_ylim(0, max_e * 1.25)
    ax1.legend(loc="upper left", framealpha=0.9, fancybox=True)

    plt.tight_layout()
    plt.savefig(str(out_file), dpi=300, bbox_inches="tight")
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

    fig, ax = plt.subplots(figsize=(12, 7))
    y_pos = np.arange(len(names))

    # Dùng lỗi bất đối xứng [avg - min, max - avg]
    err_low = np.array(avg_times) - np.array(min_times)
    err_high = np.array(max_times) - np.array(avg_times)
    yerr = [err_low, err_high]

    colors = ["#2ecc71" if "SAT" in n else ("#3498db" if "CP" in n else "#e67e22") for n in names]

    bars = ax.barh(y_pos, avg_times, xerr=yerr, align="center", color=colors, alpha=0.85, capsize=4, error_kw={"ecolor": "#555555", "linewidth": 1.2})
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.invert_yaxis()  # Đưa solver nhanh nhất hoặc đầu tiên lên trên
    ax.set_xlabel("Thời gian giải trung bình (ms)", fontsize=11)
    ax.set_title(f"So sánh thời gian giải giữa các Solver {title_suffix}", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    # Đảm bảo trục x có khoảng trống cho error bar và text
    max_val = max(max_times) if max_times else max(avg_times)
    ax.set_xlim(0, max_val * 1.15)

    for i, (bar, avg_t, min_t, max_t) in enumerate(zip(bars, avg_times, min_times, max_times)):
        # Đặt text ở vị trí an toàn sau điểm max error bar để không bao giờ bị đè vào thanh đen
        x_text = max_t + (max_val * 0.015)
        ax.text(x_text, bar.get_y() + bar.get_height() / 2,
                f"{avg_t:.2f} ms", va="center", ha="left", fontsize=9, fontweight="bold", color="#2c3e50")

    plt.tight_layout()
    plt.savefig(str(out_file), dpi=300, bbox_inches="tight")
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
    all_difficulties = ["easy", "medium", "hard", "expert"]
    diff_name_map = {"easy": "Easy", "medium": "Medium", "hard": "Hard", "expert": "Expert"}

    # Chỉ lấy những cấp độ khó THỰC SỰ CÓ DỮ LIỆU trong dataset (loại bỏ các mốc bị 0 ms)
    present_diffs = []
    for d in all_difficulties:
        if any(d in diff_scores and diff_scores[d] > 0 for diff_scores in diff_data.values()):
            present_diffs.append(d)

    if not present_diffs:
        return

    diff_labels = [diff_name_map[d] for d in present_diffs]
    fig, ax = plt.subplots(figsize=(10, 6))

    # Nếu chỉ có 2 hoặc 3 mức độ, dùng biểu đồ cột nhóm (Grouped Bar Chart) hoặc biểu đồ đường liên tục
    if len(present_diffs) <= 2:
        # Biểu đồ cột nhóm rất rõ ràng và đẹp mắt khi có 2 mức độ (ví dụ Easy vs Expert)
        methods = list(diff_data.keys())
        x = np.arange(len(present_diffs))
        n_methods = len(methods)
        width = 0.8 / n_methods

        for idx, method in enumerate(methods):
            vals = [diff_data[method].get(d, 0.0) for d in present_diffs]
            offset = (idx - (n_methods - 1) / 2) * width
            rects = ax.bar(x + offset, vals, width, label=method, alpha=0.9)
            for r in rects:
                h = r.get_height()
                if h > 0:
                    ax.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width() / 2, h),
                                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

        ax.set_xticks(x)
        ax.set_xticklabels(diff_labels, fontsize=11, fontweight="bold")
    else:
        # Biểu đồ đường (Line chart) khi có đầy đủ từ 3 đến 4 mốc độ khó liên tục
        for method, diff_scores in diff_data.items():
            y_vals = [diff_scores.get(d, 0.0) for d in present_diffs]
            ax.plot(diff_labels, y_vals, marker="o", linewidth=2.5, markersize=7, label=method)

    ax.set_xlabel("Cấp độ khó", fontsize=11, fontweight="bold")
    ax.set_ylabel("Thời gian trung bình (ms)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.9, fancybox=True)

    # Đảm bảo trục Y có khoảng trống phía trên
    y_max = ax.get_ylim()[1]
    ax.set_ylim(0, y_max * 1.18)

    plt.tight_layout()
    plt.savefig(str(out_file), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[Plotter] Đã xuất biểu đồ phân tích theo độ khó: {out_file}")
