"""
Package benchmarks: Các kịch bản đo lường hiệu năng solvers và encodings.
Hỗ trợ đo trên ma trận đơn lẻ hoặc trên tập dataset chuẩn hóa từ KaggleHub và Hugging Face.
"""

from .benchmark_solvers import run_benchmark as benchmark_solvers
from .benchmark_encodings import benchmark_encodings
from .dataset_loader import (
    load_from_kagglehub,
    load_from_huggingface,
    prepare_benchmark_dataset,
    load_normalized_dataset,
    normalize_puzzle,
    string_to_grid,
    grid_to_string,
)
from .benchmark_dataset import (
    benchmark_dataset_solvers,
    benchmark_dataset_encodings,
)
from .plotter import (
    plot_encodings_benchmark,
    plot_solvers_benchmark,
    plot_difficulty_comparison,
)

__all__ = [
    "benchmark_solvers",
    "benchmark_encodings",
    "benchmark_dataset_solvers",
    "benchmark_dataset_encodings",
    "plot_encodings_benchmark",
    "plot_solvers_benchmark",
    "plot_difficulty_comparison",
    "load_from_kagglehub",
    "load_from_huggingface",
    "prepare_benchmark_dataset",
    "load_normalized_dataset",
    "normalize_puzzle",
    "string_to_grid",
    "grid_to_string",
]
