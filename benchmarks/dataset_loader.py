"""
Module dataset_loader: Tải và chuẩn hóa dữ liệu Sudoku từ KaggleHub và Hugging Face.

Hỗ trợ các định dạng đầu vào:
- Chuỗi 81 ký tự (0-9 hoặc dấu chấm '.') từ Kaggle (gaz3ll3/top95-sudoku, bryanpark/sudoku)
  hoặc Hugging Face (Ritvik19/Sudoku-Dataset).
- Ma trận 9x9 2D List từ Hugging Face (Alignment-Lab-AI/Expert-Sudoku-100k, MathMindsAGI/sudoku_v1).
- Danh sách 81 phần tử dạng flat list / JSON array.

Dữ liệu được chuẩn hóa về định dạng thống nhất:
{
    "id": str,
    "source": "kagglehub" | "huggingface",
    "dataset": str,
    "difficulty": "easy" | "medium" | "hard" | "expert",
    "clues_count": int,
    "puzzle_string": str (81 chars),
    "grid": List[List[int]] (9x9),
    "solution_string": Optional[str],
    "solution_grid": Optional[List[List[int]]]
}
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Đường dẫn mặc định lưu dữ liệu chuẩn hóa
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DATASET_PATH = DATA_DIR / "benchmark_dataset.json"


def string_to_grid(puzzle_str: str) -> List[List[int]]:
    """
    Chuyển chuỗi puzzle thành ma trận N x N (hỗ trợ 4x4=16, 9x9=81, 16x16=256).
    """
    if not isinstance(puzzle_str, str):
        puzzle_str = str(puzzle_str)

    clean_str = puzzle_str.strip().replace(".", "0")
    length = len(clean_str)
    
    # Xác định kích thước N từ độ dài chuỗi
    import math
    N = math.isqrt(length)
    if N * N != length:
        raise ValueError(f"Chuỗi Sudoku có độ dài {length} không phải là bình phương hoàn hảo (NxN).")

    grid: List[List[int]] = []
    for r in range(N):
        row = []
        for c in range(N):
            ch = clean_str[r * N + c]
            if ch.isdigit():
                val = int(ch)
            else:
                # Hỗ trợ ký tự Hexadoku (A=10..G=16)
                val = ord(ch.upper()) - ord('A') + 10
            row.append(val)
        grid.append(row)
    return grid


def grid_to_string(grid: List[List[int]]) -> str:
    """
    Chuyển ma trận N x N thành chuỗi.
    """
    if not grid or not isinstance(grid, list):
        raise ValueError("Ma trận Sudoku không hợp lệ.")
    N = len(grid)
    chars = []
    for row in grid:
        for val in row:
            if val == 0:
                chars.append("0")
            elif 1 <= val <= 9:
                chars.append(str(val))
            elif 10 <= val <= 36:
                chars.append(chr(ord('A') + val - 10))
            else:
                chars.append("?")
    return "".join(chars)


def infer_difficulty(clues_count: int, N: int = 9, explicit_label: Optional[str] = None) -> str:
    """
    Chuẩn hóa cấp độ khó của Sudoku dựa trên tỷ lệ ô gợi ý (Clue Density) và kích thước N:
    - expert: Tỷ lệ clues <= 27% (ít gợi ý, suy luận sâu)
    - hard: 28% - 33%
    - medium: 34% - 42%
    - easy: >= 43% (nhiều gợi ý)
    """
    total_cells = N * N
    ratio = clues_count / total_cells if total_cells > 0 else 0.3

    if explicit_label:
        label = str(explicit_label).strip().lower()
        if label in ["expert", "evil", "diabolical", "extreme"]:
            return "expert"
        if label in ["hard", "difficult"]:
            return "hard"
        if label in ["medium", "normal", "moderate"]:
            return "medium"
        if label in ["easy", "simple", "beginner"]:
            if ratio <= 0.32:
                return "hard"
            elif ratio <= 0.40:
                return "medium"
            return "easy"

    if ratio <= 0.27:
        return "expert"
    elif ratio <= 0.33:
        return "hard"
    elif ratio <= 0.42:
        return "medium"
    else:
        return "easy"


def normalize_puzzle(
    raw_puzzle: Union[str, List[int], List[List[int]]],
    puzzle_id: str,
    source: str,
    dataset: str,
    raw_solution: Optional[Union[str, List[int], List[List[int]]]] = None,
    difficulty: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Chuẩn hóa bất kỳ định dạng Sudoku nào (4x4, 9x9, 16x16,...) thành schema thống nhất.
    """
    # 1. Chuẩn hóa puzzle grid và string
    if isinstance(raw_puzzle, str):
        p_str = raw_puzzle.strip().replace(".", "0")
        p_grid = string_to_grid(p_str)
    elif isinstance(raw_puzzle, list):
        if len(raw_puzzle) > 0 and isinstance(raw_puzzle[0], list):
            # Ma trận 2D N x N
            N = len(raw_puzzle)
            p_grid = [[int(cell) for cell in row] for row in raw_puzzle]
            p_str = grid_to_string(p_grid)
        else:
            # Danh sách phẳng
            import math
            N = math.isqrt(len(raw_puzzle))
            p_grid = [[int(raw_puzzle[r * N + c]) for c in range(N)] for r in range(N)]
            p_str = grid_to_string(p_grid)
    else:
        raise TypeError(f"Kiểu dữ liệu puzzle không được hỗ trợ: {type(raw_puzzle)}")

    N = len(p_grid)
    # 2. Đếm số gợi ý (clues)
    clues_count = sum(1 for row in p_grid for cell in row if cell != 0)

    # 3. Chuẩn hóa solution (nếu có)
    s_str: Optional[str] = None
    s_grid: Optional[List[List[int]]] = None
    if raw_solution is not None:
        try:
            if isinstance(raw_solution, str):
                s_str = raw_solution.strip().replace(".", "0")
                s_grid = string_to_grid(s_str)
            elif isinstance(raw_solution, list):
                if len(raw_solution) > 0 and isinstance(raw_solution[0], list):
                    s_grid = [[int(cell) for cell in row] for row in raw_solution]
                    s_str = grid_to_string(s_grid)
                else:
                    s_grid = [[int(raw_solution[r * N + c]) for c in range(N)] for r in range(N)]
                    s_str = grid_to_string(s_grid)
        except Exception:
            s_str = None
            s_grid = None

    # 4. Xác định độ khó chuẩn hóa
    norm_diff = infer_difficulty(clues_count, N=N, explicit_label=difficulty)

    return {
        "id": puzzle_id,
        "source": source,
        "dataset": dataset,
        "size": N,
        "difficulty": norm_diff,
        "clues_count": clues_count,
        "puzzle_string": p_str,
        "grid": p_grid,
        "solution_string": s_str,
        "solution_grid": s_grid,
    }


def load_from_kagglehub(
    dataset_name: str = "gaz3ll3/top95-sudoku",
    limit: int = 10,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Tải và chuẩn hóa dataset từ KaggleHub.
    Hỗ trợ:
    - 'gaz3ll3/top95-sudoku': Bộ 95 bài Sudoku kinh điển cho benchmark.
    - 'bryanpark/sudoku': Bộ 1 triệu bài Sudoku từ Kaggle.
    """
    import kagglehub
    import pandas as pd

    print(f"[KaggleHub] Đang kiểm tra/tải dataset '{dataset_name}'...")
    download_path = kagglehub.dataset_download(dataset_name)
    print(f"[KaggleHub] Dataset nằm tại: {download_path}")

    puzzles: List[Dict[str, Any]] = []

    # Tìm file CSV trong thư mục dataset
    csv_files = [f for f in os.listdir(download_path) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError(f"Không tìm thấy file .csv nào trong {download_path}")

    csv_path = os.path.join(download_path, csv_files[0])
    # Đọc với dtype=str để không bị mất số 0 đầu và tránh overflow
    df = pd.read_csv(csv_path, dtype=str)

    # Nhận diện cột quiz và solution
    quiz_col = next((c for c in ["quizzes", "puzzle", "quizz", "quiz", "sudoku"] if c in df.columns), df.columns[0])
    sol_col = next((c for c in ["solutions", "solution", "solved"] if c in df.columns), None)

    total_rows = len(df)
    end_idx = min(offset + limit, total_rows)

    for i in range(offset, end_idx):
        row = df.iloc[i]
        raw_quiz = str(row[quiz_col])
        raw_sol = str(row[sol_col]) if sol_col else None

        puzzle_id = f"kaggle_{dataset_name.split('/')[-1]}_{i + 1:04d}"
        normalized = normalize_puzzle(
            raw_puzzle=raw_quiz,
            puzzle_id=puzzle_id,
            source="kagglehub",
            dataset=dataset_name,
            raw_solution=raw_sol,
        )
        puzzles.append(normalized)

    print(f"[KaggleHub] Đã tải và chuẩn hóa {len(puzzles)} puzzles từ '{dataset_name}'.")
    return puzzles


def load_from_huggingface(
    dataset_name: str = "Ritvik19/Sudoku-Dataset",
    split: str = "validation",
    limit: int = 10,
    difficulty_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Tải và chuẩn hóa dataset từ Hugging Face bằng Streaming API.
    Hỗ trợ:
    - 'Ritvik19/Sudoku-Dataset': Tập 17M puzzles tổng hợp lớn nhất (split: 'validation' hoặc 'train').
    - 'Alignment-Lab-AI/Expert-Sudoku-100k': Tập chuyên các bài độ khó cao 'expert' (split: 'train').
    - 'MathMindsAGI/sudoku_v1': Tập dạng ma trận 9x9 (split: 'train').
    """
    from datasets import load_dataset

    print(f"[HuggingFace] Đang stream dữ liệu từ '{dataset_name}' (split='{split}')...")
    ds = load_dataset(dataset_name, split=split, streaming=True)

    puzzles: List[Dict[str, Any]] = []
    idx = 0

    for item in ds:
        # Nhận diện định dạng từng dataset trên HF
        if "puzzle" in item:
            # Ritvik19 schema
            raw_quiz = item["puzzle"]
            raw_sol = item.get("solution")
            diff = item.get("difficulty")
        elif "input" in item:
            # Alignment-Lab-AI/Expert schema
            raw_quiz = item["input"]
            raw_sol = item.get("output")
            diff = item.get("difficulty")
        elif "grid" in item:
            # MathMindsAGI schema
            raw_quiz = item["grid"]
            raw_sol = item.get("solution")
            diff = item.get("difficulty")
        else:
            # Thử lấy 2 key đầu tiên
            keys = list(item.keys())
            raw_quiz = item[keys[0]]
            raw_sol = item[keys[1]] if len(keys) > 1 else None
            diff = None

        puzzle_id = f"hf_{dataset_name.split('/')[-1]}_{idx + 1:04d}"
        try:
            normalized = normalize_puzzle(
                raw_puzzle=raw_quiz,
                puzzle_id=puzzle_id,
                source="huggingface",
                dataset=dataset_name,
                raw_solution=raw_sol,
                difficulty=str(diff) if diff is not None else None,
            )

            if difficulty_filter and normalized["difficulty"] != difficulty_filter:
                continue

            puzzles.append(normalized)
            idx += 1
            if len(puzzles) >= limit:
                break
        except Exception as e:
            continue

    print(f"[HuggingFace] Đã tải và chuẩn hóa {len(puzzles)} puzzles từ '{dataset_name}'.")
    return puzzles


def get_default_fallback_puzzles() -> List[Dict[str, Any]]:
    """
    Dữ liệu dự phòng phong phú từ các bài benchmark nổi tiếng
    (trong trường hợp máy không có kết nối internet hoặc cần chạy offline).
    """
    raw_samples = [
        {
            "id": "kaggle_top95_0001",
            "source": "kagglehub",
            "dataset": "gaz3ll3/top95-sudoku",
            "difficulty": "expert",
            "puzzle": "400000805030000000000700000020000060000080400000010000000603070500200000104000000",
            "solution": "417369825632158947958724316825437169791586432346912758289643571573291684164875293"
        },
        {
            "id": "kaggle_top95_0002",
            "source": "kagglehub",
            "dataset": "gaz3ll3/top95-sudoku",
            "difficulty": "expert",
            "puzzle": "520006000000000701300000000000400800600000050000000000041800000000030020008700000",
            "solution": "527316489896542731314987562172453896689271354435698217941825673758134920268769145"
        },
        {
            "id": "hf_ritvik19_0001",
            "source": "huggingface",
            "dataset": "Ritvik19/Sudoku-Dataset",
            "difficulty": "medium",
            "puzzle": "107930864048127590905048712370009620286001045409206137804700301700013089513094006",
            "solution": "127935864648127593935648712371459628286371945459286137894762351762513489513894276"
        },
        {
            "id": "hf_ritvik19_0002",
            "source": "huggingface",
            "dataset": "Ritvik19/Sudoku-Dataset",
            "difficulty": "hard",
            "puzzle": "296001008850003600000090201905700000087002940000000010030000025470320109560007483",
            "solution": "296541378851273694743698251915764832387152946624839517139486725478325169562917483"
        },
        {
            "id": "hf_expert_0001",
            "source": "huggingface",
            "dataset": "Alignment-Lab-AI/Expert-Sudoku-100k",
            "difficulty": "expert",
            "puzzle": "000900004053207008090050301436000000020000060578000000040020106065309002000400007",
            "solution": "687931524153247698294658371436892715921574863578163249849725136765319482312486957"
        },
        {
            "id": "kaggle_classic_17clue",
            "source": "kagglehub",
            "dataset": "bryanpark/sudoku",
            "difficulty": "expert",
            "puzzle": "000000010400000000020000000000050407008000300001090000300400200050100000000806000",
            "solution": "693784512487512936125963874932658427578241369841397258316475298254139786789826143"
        }
    ]

    puzzles = []
    for item in raw_samples:
        p = normalize_puzzle(
            raw_puzzle=item["puzzle"],
            puzzle_id=item["id"],
            source=item["source"],
            dataset=item["dataset"],
            raw_solution=item.get("solution"),
            difficulty=item.get("difficulty"),
        )
        puzzles.append(p)
    return puzzles


def load_from_norvig_benchmark(limit_per_category: int = 50) -> List[Dict[str, Any]]:
    """
    Tải trực tiếp các bộ Sudoku benchmark kinh điển của Peter Norvig (top95, easy50, hardest)
    thông qua urllib chuẩn, không cần phụ thuộc thư viện ngoài.
    """
    import urllib.request

    sources = [
        ("top95", "https://norvig.com/top95.txt", None, limit_per_category),
        ("easy50", "https://norvig.com/easy50.txt", None, limit_per_category),
        ("hardest", "https://norvig.com/hardest.txt", "expert", limit_per_category),
    ]

    puzzles: List[Dict[str, Any]] = []

    for name, url, default_diff, limit in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8", errors="ignore")
                
                added = 0
                # Trường hợp dạng khối phân tách bằng ======== (như easy50.txt)
                if "========" in content:
                    blocks = [b.strip() for b in content.split("========") if b.strip()]
                    for b in blocks:
                        # Gom 9 dòng thành chuỗi 81 ký tự
                        rows = [r.strip().replace(".", "0") for r in b.splitlines() if r.strip() and not r.strip().startswith("#")]
                        if len(rows) == 9 and all(len(r) == 9 for r in rows):
                            puzzle_str = "".join(rows)
                            p_id = f"norvig_{name}_{added + 1:04d}"
                            norm = normalize_puzzle(
                                raw_puzzle=puzzle_str,
                                puzzle_id=p_id,
                                source="norvig",
                                dataset=f"norvig/{name}",
                                difficulty=default_diff,
                            )
                            puzzles.append(norm)
                            added += 1
                            if added >= limit:
                                break
                else:
                    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#") and not line.startswith("=")]
                    for line in lines:
                        clean = line.replace(".", "0")
                        if len(clean) >= 81:
                            puzzle_str = clean[:81]
                            if all(c in "0123456789" for c in puzzle_str):
                                p_id = f"norvig_{name}_{added + 1:04d}"
                                norm = normalize_puzzle(
                                raw_puzzle=puzzle_str,
                                puzzle_id=p_id,
                                source="norvig",
                                dataset=f"norvig/{name}",
                                difficulty=default_diff,
                            )
                            puzzles.append(norm)
                            added += 1
                            if added >= limit:
                                break
                print(f"[Norvig Benchmark] Đã tải thành công {added} bài từ '{name}'.")
        except Exception as e:
            print(f"[Norvig Benchmark] Không thể tải '{name}' ({e}). Bỏ qua.")

    return puzzles


def load_from_sudoku_exchange_bank(limit_per_category: int = 40) -> List[Dict[str, Any]]:
    """
    Tải trực tiếp các bài Sudoku từ ngân hàng câu đố Sudoku Exchange (hỗ trợ easy, medium, hard, diabolical).
    Đây là nguồn chuẩn mực cung cấp đầy đủ các cấp độ khó khác nhau.
    """
    import urllib.request

    sources = [
        ("easy", "https://raw.githubusercontent.com/grantm/sudoku-exchange-puzzle-bank/master/easy.txt", "easy"),
        ("medium", "https://raw.githubusercontent.com/grantm/sudoku-exchange-puzzle-bank/master/medium.txt", "medium"),
        ("hard", "https://raw.githubusercontent.com/grantm/sudoku-exchange-puzzle-bank/master/hard.txt", "hard"),
        ("diabolical", "https://raw.githubusercontent.com/grantm/sudoku-exchange-puzzle-bank/master/diabolical.txt", "expert"),
    ]

    puzzles: List[Dict[str, Any]] = []

    for name, url, diff_label in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                added = 0
                for _ in range(limit_per_category * 2):
                    line = response.readline().decode("utf-8", errors="ignore").strip()
                    if not line:
                        break
                    parts = line.split()
                    if len(parts) >= 2:
                        p_str = parts[1]
                        if len(p_str) == 81 and all(c in "0123456789." for c in p_str):
                            p_id = f"exchange_{name}_{added + 1:04d}"
                            norm = normalize_puzzle(
                                raw_puzzle=p_str,
                                puzzle_id=p_id,
                                source="sudoku_exchange",
                                dataset=f"sudoku_exchange/{name}",
                                difficulty=diff_label,
                            )
                            puzzles.append(norm)
                            added += 1
                            if added >= limit_per_category:
                                break
                print(f"[Sudoku Exchange] Đã tải thành công {added} bài độ khó '{name}'.")
        except Exception as e:
            print(f"[Sudoku Exchange] Không thể tải '{name}' ({e}).")

    return puzzles


def get_multisize_puzzles() -> List[Dict[str, Any]]:
    """
    Tập hợp các bài Sudoku kích thước đa dạng (4x4 Mini-Sudoku và 16x16 Hexadoku)
    đáp ứng yêu cầu 'thực nghiệm với các ma trận có kích thước lớn' của đề bài.
    """
    multisize: List[Dict[str, Any]] = []

    # 1. Tập các bài Sudoku 4x4
    grids_4x4 = [
        # Easy / Medium / Hard 4x4
        ([[1, 0, 3, 0], [0, 0, 0, 1], [4, 0, 0, 0], [0, 2, 0, 4]], "medium"),
        ([[0, 2, 0, 0], [0, 0, 1, 0], [0, 3, 0, 0], [0, 0, 4, 0]], "hard"),
        ([[1, 2, 3, 0], [3, 4, 0, 0], [2, 0, 4, 0], [0, 0, 0, 0]], "easy"),
        ([[0, 0, 0, 4], [0, 0, 3, 0], [0, 1, 0, 0], [2, 0, 0, 0]], "expert"),
        ([[0, 1, 0, 0], [4, 0, 0, 0], [0, 0, 0, 2], [0, 0, 3, 0]], "hard"),
        ([[0, 0, 3, 4], [3, 4, 0, 0], [0, 0, 4, 3], [4, 3, 0, 0]], "medium"),
        ([[2, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [4, 0, 0, 3]], "expert"),
        ([[1, 0, 0, 4], [0, 2, 3, 0], [0, 3, 2, 0], [4, 0, 0, 1]], "easy"),
        ([[0, 0, 0, 0], [0, 1, 2, 0], [0, 3, 4, 0], [0, 0, 0, 0]], "expert"),
        ([[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 4]], "expert"),
    ]

    for idx, (g, diff) in enumerate(grids_4x4):
        multisize.append(normalize_puzzle(
            raw_puzzle=g,
            puzzle_id=f"matrix4x4_{idx + 1:04d}",
            source="benchmark_multisize",
            dataset="synthetic_4x4",
            difficulty=diff,
        ))

    # 2. Tập các bài Sudoku 16x16 (Hexadoku)
    # Khởi tạo ma trận cơ sở 16x16 hợp lệ
    base_16 = [
        [ 1,  2,  3,  4,   5,  6,  7,  8,   9, 10, 11, 12,  13, 14, 15, 16],
        [ 5,  6,  7,  8,   9, 10, 11, 12,  13, 14, 15, 16,   1,  2,  3,  4],
        [ 9, 10, 11, 12,  13, 14, 15, 16,   1,  2,  3,  4,   5,  6,  7,  8],
        [13, 14, 15, 16,   1,  2,  3,  4,   5,  6,  7,  8,   9, 10, 11, 12],

        [ 2,  3,  4,  1,   6,  7,  8,  5,  10, 11, 12,  9,  14, 15, 16, 13],
        [ 6,  7,  8,  5,  10, 11, 12,  9,  14, 15, 16, 13,   2,  3,  4,  1],
        [10, 11, 12,  9,  14, 15, 16, 13,   2,  3,  4,  1,   6,  7,  8,  5],
        [14, 15, 16, 13,   2,  3,  4,  1,   6,  7,  8,  5,  10, 11, 12,  9],

        [ 3,  4,  1,  2,   7,  8,  5,  6,  11, 12,  9, 10,  15, 16, 13, 14],
        [ 7,  8,  5,  6,  11, 12,  9, 10,  15, 16, 13, 14,   3,  4,  1,  2],
        [11, 12,  9, 10,  15, 16, 13, 14,   3,  4,  1,  2,   7,  8,  5,  6],
        [15, 16, 13, 14,   3,  4,  1,  2,   7,  8,  5,  6,  11, 12,  9, 10],

        [ 4,  1,  2,  3,   8,  5,  6,  7,  12,  9, 10, 11,  16, 13, 14, 15],
        [ 8,  5,  6,  7,  12,  9, 10, 11,  16, 13, 14, 15,   4,  1,  2,  3],
        [12,  9, 10, 11,  16, 13, 14, 15,   4,  1,  2,  3,   8,  5,  6,  7],
        [16, 13, 14, 15,   4,  1,  2,  3,   8,  5,  6,  7,  12,  9, 10, 11],
    ]

    # Sinh các bài 16x16 với các tỷ lệ đục lỗ khác nhau để tạo cấp độ khó từ Easy đến Expert
    import random
    rng = random.Random(42)
    rates = [
        (0.55, "easy"),    # 55% clues
        (0.48, "easy"),
        (0.40, "medium"),  # 40% clues
        (0.35, "medium"),
        (0.30, "hard"),    # 30% clues
        (0.28, "hard"),
        (0.25, "expert"),  # 25% clues
        (0.22, "expert"),
        (0.20, "expert"),
        (0.18, "expert"),
    ]

    for idx, (rate, diff) in enumerate(rates):
        grid_copy = [row[:] for row in base_16]
        # Xóa các ô ngẫu nhiên đối xứng
        total_to_remove = int(256 * (1.0 - rate))
        indices = list(range(256))
        rng.shuffle(indices)
        for k in range(total_to_remove):
            r = indices[k] // 16
            c = indices[k] % 16
            grid_copy[r][c] = 0

        multisize.append(normalize_puzzle(
            raw_puzzle=grid_copy,
            puzzle_id=f"hexadoku16x16_{idx + 1:04d}",
            source="benchmark_multisize",
            dataset="synthetic_16x16",
            difficulty=diff,
        ))

    return multisize


def prepare_benchmark_dataset(
    output_path: Union[str, Path] = DEFAULT_DATASET_PATH,
    kaggle_limit: int = 50,
    hf_limit: int = 50,
    norvig_limit: int = 50,
    force_download: bool = False,
) -> List[Dict[str, Any]]:
    """
    Thu thập và chuẩn hóa dataset tổng hợp từ Norvig Benchmark, KaggleHub và Hugging Face,
    lưu trữ tại file JSON để toàn bộ project có thể sử dụng mượt mà.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Nếu đã tồn tại file và không ép tải lại, đọc từ cache
    if output_path.exists() and not force_download:
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if isinstance(cached, list) and len(cached) > 0:
                    print(f"[Dataset] Đã tải {len(cached)} puzzles chuẩn hóa từ cache: {output_path}")
                    return cached
        except Exception as e:
            print(f"[Dataset] Lỗi đọc cache ({e}), tiến hành tải mới...")

    print("=" * 72)
    print("CHUẨN HÓA DỮ LIỆU BENCHMARK TỪ NORVIG, KAGGLEHUB VÀ HUGGING FACE")
    print("=" * 72)

    all_puzzles: List[Dict[str, Any]] = []

    # 1. Tải từ Norvig Benchmark (top95, easy50, hardest)
    norvig_puzzles = load_from_norvig_benchmark(limit_per_category=norvig_limit)
    if norvig_puzzles:
        all_puzzles.extend(norvig_puzzles)

    # 2. Tải từ Sudoku Exchange Puzzle Bank (Đa dạng 4 cấp độ: Easy, Medium, Hard, Diabolical/Expert)
    try:
        exchange_puzzles = load_from_sudoku_exchange_bank(limit_per_category=40)
        if exchange_puzzles:
            all_puzzles.extend(exchange_puzzles)
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể tải từ Sudoku Exchange ({e}).")

    # 3. Thêm các bài Sudoku kích thước đa dạng (4x4, 16x16)
    try:
        multisize_puzzles = get_multisize_puzzles()
        all_puzzles.extend(multisize_puzzles)
        print(f"[Multisize] Đã tích hợp {len(multisize_puzzles)} bài Sudoku kích thước 4x4 và 16x16 Hexadoku.")
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể khởi tạo multisize puzzles ({e}).")

    # 4. Tải từ KaggleHub (Bộ Top95 benchmark kinh điển)
    try:
        kaggle_puzzles = load_from_kagglehub(
            dataset_name="gaz3ll3/top95-sudoku",
            limit=kaggle_limit,
            offset=0
        )
        all_puzzles.extend(kaggle_puzzles)
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể tải từ KaggleHub ({e}). Tiếp tục...")

    # 5. Tải từ Hugging Face (Bộ Ritvik19/Sudoku-Dataset)
    try:
        hf_puzzles = load_from_huggingface(
            dataset_name="Ritvik19/Sudoku-Dataset",
            split="validation",
            limit=hf_limit
        )
        all_puzzles.extend(hf_puzzles)
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể tải từ HF Ritvik19 ({e}).")

    # 4. Nếu vẫn trống, dùng bộ fallback phong phú
    if not all_puzzles:
        print("[Dataset] Không kết nối được internet, sử dụng bộ dữ liệu chuẩn hóa dự phòng (Offline Fallback)...")
        all_puzzles = get_default_fallback_puzzles()

    # Ghi dữ liệu chuẩn hóa ra JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_puzzles, f, indent=2, ensure_ascii=False)

    print(f"[Dataset] Đã lưu thành công {len(all_puzzles)} bài Sudoku chuẩn hóa tại: {output_path}")
    print("=" * 72)
    return all_puzzles


def load_normalized_dataset(
    dataset_path: Union[str, Path] = DEFAULT_DATASET_PATH,
    source: Optional[str] = None,
    difficulty: Optional[str] = None,
    size: Optional[Union[int, str]] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Đọc dữ liệu chuẩn hóa đã chuẩn bị sẵn và lọc theo điều kiện (source, difficulty, size, limit).
    """
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        puzzles = prepare_benchmark_dataset(output_path=dataset_path)
    else:
        with open(dataset_path, "r", encoding="utf-8") as f:
            puzzles = json.load(f)

    filtered = puzzles
    if size is not None and str(size).lower() != "all":
        target_size = int(size)
        filtered = [p for p in filtered if p.get("size", len(p.get("grid", []))) == target_size]

    if source and source.lower() != "all":
        src_query = source.lower()
        filtered = [p for p in filtered if src_query in p["source"].lower() or src_query in p["dataset"].lower()]

    if difficulty and difficulty.lower() != "all":
        diff_query = difficulty.lower()
        filtered = [p for p in filtered if p["difficulty"].lower() == diff_query]

    if limit is not None and limit > 0:
        if difficulty is None or difficulty.lower() == "all":
            # Phân bổ đều các cấp độ khó khác nhau (easy, medium, hard, expert)
            # để đảm bảo tập test có tính đại diện và kích hoạt được phân tích theo độ khó
            from collections import defaultdict
            by_diff = defaultdict(list)
            for p in filtered:
                by_diff[p.get("difficulty", "unknown")].append(p)
            
            diff_keys = list(by_diff.keys())
            if len(diff_keys) > 1:
                balanced = []
                per_diff = max(1, limit // len(diff_keys))
                for k in diff_keys:
                    balanced.extend(by_diff[k][:per_diff])
                # Nếu còn thiếu do phép chia nguyên, bổ sung thêm
                rem = limit - len(balanced)
                if rem > 0:
                    used_ids = {p.get("id") for p in balanced}
                    for p in filtered:
                        if p.get("id") not in used_ids:
                            balanced.append(p)
                            if len(balanced) >= limit:
                                break
                filtered = balanced[:limit]
            else:
                filtered = filtered[:limit]
        else:
            filtered = filtered[:limit]

    return filtered


if __name__ == "__main__":
    prepare_benchmark_dataset(force_download=True)
