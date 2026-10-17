# Sudoku Solver & SAT Cardinality Encodings (AMO / ALO Framework)

Dự án triển khai và benchmark các thuật toán giải Sudoku tổng quát $N \times N$ (4x4, 9x9, 16x16,...) với trọng tâm là **các kỹ thuật mã hóa SAT cho ràng buộc số lượng (Cardinality Constraints: At-Most-One - AMO, At-Least-One - ALO, Exactly-One - EO)**, đồng thời so sánh hiệu năng với các phương pháp giải tối ưu khác như Constraint Programming (CP) và Integer Linear Programming (ILP/MIP).

Dự án tích hợp trực tiếp các bộ dữ liệu Sudoku lớn và chuẩn mực từ **KaggleHub** và **Hugging Face**, thực hiện quy trình chuẩn hóa dữ liệu thống nhất (Data Normalization Pipeline) để phục vụ đo lường và đánh giá toàn diện.

---

## 1. Cấu trúc dự án chuẩn mực & logic

```text
Sudoku_prj/
├── data/                         # Thư mục chứa dữ liệu chuẩn hóa
│   └── benchmark_dataset.json   # Dataset benchmark tổng hợp từ KaggleHub & Hugging Face
│
├── sat_encodings/               # Các phương pháp mã hóa SAT cho ALO, AMO, EO (generic cho mọi n)
│   ├── __init__.py              # Public API
│   ├── alo.py                   # At-Least-One: (x1 v x2 v ... v xn)
│   ├── pairwise.py              # Pairwise AMO (Naive O(n^2))
│   ├── binary.py                # Binary / Bitwise AMO qua PySAT (Frisch et al., 2005)
│   ├── commander.py             # Commander AMO (Klieber & Kwon, 2007)
│   ├── product.py               # 2-Product AMO (Jingchao Chen, 2010)
│   ├── seqcounter.py            # Sequential Counter AMO qua PySAT (Sinz, 2005)
│   └── manager.py               # Bộ điều phối (Dispatcher: at_most_one, exactly_one)
│
├── solvers/                     # Các bộ giải Sudoku đa phương pháp (Hỗ trợ tổng quát NxN)
│   ├── __init__.py              # Public solver API
│   ├── sat_solver.py            # SAT Solver (Glucose3) hỗ trợ chuyển đổi đa dạng encodings
│   ├── cpsat_solver.py          # Google OR-Tools CP-SAT Solver
│   ├── ilp_solver.py            # PuLP / CBC ILP Solver
│   ├── gurobi_solver.py         # Gurobi Optimizer (MIP)
│   ├── cplex_cp_solver.py       # IBM CPLEX CP Optimizer
│   └── cplex_mip_solver.py      # IBM CPLEX MIP Solver
│
├── benchmarks/                  # Scripts đo lường hiệu năng
│   ├── __init__.py              # Public benchmark & loader API
│   ├── dataset_loader.py        # Tải và chuẩn hóa dataset từ KaggleHub & Hugging Face
│   ├── benchmark_dataset.py     # Benchmark Solvers & Encodings trên Dataset chuẩn hóa
│   ├── benchmark_solvers.py     # So sánh tất cả các Solver trên ma trận mẫu
│   └── benchmark_encodings.py   # So sánh 5 phương pháp SAT Encoding trên ma trận mẫu
│
├── tests/                       # Hệ thống kiểm thử tự động
│   ├── __init__.py
│   ├── test_encodings.py        # Kiểm thử tính đúng đắn chân trị (Soundness & Completeness)
│   ├── test_solvers.py          # Kiểm thử tích hợp kiểm tra nghiệm các solver trên 4x4, 9x9, 16x16
│   └── test_dataset.py          # Kiểm thử loader & chuẩn hóa dữ liệu (string/grid/formats)
│
├── utils.py                     # Đề bài mẫu (4x4, 9x9, 16x16) & hiển thị bảng Sudoku NxN
├── main.py                      # Điểm vào dòng lệnh (CLI Application hỗ trợ đầy đủ tính năng)
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn
```

---

## 2. Dữ liệu Benchmark từ KaggleHub & Hugging Face

### 2.1. Nguồn Dataset tích hợp
1. **KaggleHub**:
   - `gaz3ll3/top95-sudoku`: Bộ 95 bài Sudoku kinh điển và thách thức nhất (Top 95 benchmark collection) thường được dùng trong các nghiên cứu khoa học và cộng đồng Sudoku quốc tế (Peter Norvig).
   - Hỗ trợ mở rộng `bryanpark/sudoku` (1 triệu ván Sudoku trên Kaggle).
2. **Hugging Face**:
   - `Ritvik19/Sudoku-Dataset`: Tập dữ liệu 17 triệu bài Sudoku lớn nhất tổng hợp từ nhiều nguồn uy tín, hỗ trợ stream trực tiếp phân vùng validation/train.
   - `Alignment-Lab-AI/Expert-Sudoku-100k`: Tập dữ liệu 100,000 bài Sudoku chuyên biệt cấp độ khó cao (Expert/Hard).
   - `MathMindsAGI/sudoku_v1`: Bộ dữ liệu định dạng ma trận chuẩn 9x9.

### 2.2. Chuẩn hóa dữ liệu (Data Normalization Pipeline)
Dữ liệu từ các nền tảng khác nhau có các định dạng không đồng nhất (chuỗi 81 ký tự số, ký tự dấu chấm `.` thay cho ô trống, danh sách phẳng 81 phần tử, hoặc mảng 2 chiều 9x9). 

Module `benchmarks/dataset_loader.py` tự động chuyển đổi tất cả về schema chuẩn duy nhất:
```json
{
  "id": "kaggle_top95-sudoku_0001",
  "source": "kagglehub",
  "dataset": "gaz3ll3/top95-sudoku",
  "difficulty": "expert",
  "clues_count": 17,
  "puzzle_string": "400000805030000000000700000020000060000080400000010000000603070500200000104000000",
  "grid": [[4, 0, 0, ...], ...],
  "solution_string": "417369825632158947...",
  "solution_grid": [[4, 1, 7, ...], ...]
}
```

Phân loại cấp độ khó chuẩn hóa (`infer_difficulty`):
- **Expert**: $\le 22$ gợi ý (clues) ban đầu (bao gồm dạng tối thiểu 17-clue) hoặc nhãn Diabolical/Expert.
- **Hard**: $23 - 27$ gợi ý.
- **Medium**: $28 - 35$ gợi ý.
- **Easy**: $\ge 36$ gợi ý.

---

## 3. Bảng so sánh các phương pháp mã hóa AMO

| Phương pháp AMO | Thư viện / Tác giả | Biến phụ | Số Clauses | Ưu điểm & Nhược điểm |
| :--- | :--- | :--- | :--- | :--- |
| **Pairwise (Naive)** | Tổ hợp $\binom{n}{2}$ | $0$ | $O(n^2)$ | Dễ cài đặt, không biến phụ, nhưng bùng nổ clause khi $n$ lớn. |
| **Binary (Bitwise)** | PySAT (`EncType.bitwise`) | $\lceil \log_2 n \rceil$ | $O(n \log n)$ | Rất ít biến phụ, số clause tăng theo logarit. |
| **Commander** | Klieber & Kwon (2007) | $O(n/k)$ | $O(n)$ | Tuyến tính cả biến và mệnh đề, chia cụm $k \le 3$ trực quan. |
| **Product (2-Product)**| Jingchao Chen (2010) | $2\lceil\sqrt{n}\rceil$ | $O(n)$ | Mã hóa cực nhanh $O(1)$, cấu trúc lưới 2 chiều thanh lịch. |
| **Sequential Counter**| PySAT (`EncType.seqcounter`) | $n - 1$ | $O(n)$ ($\sim 3n-4$) | Tối ưu hóa lan truyền đơn vị (unit propagation) của SAT solver. |

---

## 4. Hướng dẫn sử dụng CLI (`main.py`)

### 4.1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 4.2. Tải và chuẩn hóa Dataset từ KaggleHub & Hugging Face
```bash
# Tải và chuẩn hóa dữ liệu từ cả 2 nguồn, lưu vào data/benchmark_dataset.json:
python main.py --prepare-data
```

### 4.3. Chạy Benchmark trên Dataset chuẩn hóa
```bash
# 1. Chạy toàn bộ benchmark (cả 5 SAT Encodings và tất cả Solvers) trên dataset:
python main.py --benchmark-dataset

# 2. Giới hạn số lượng bài cần test (ví dụ 10 bài):
python main.py --benchmark-dataset --limit 10

# 3. Benchmark các Solver trên dataset:
python main.py --benchmark-dataset-solvers

# 4. Benchmark các phương pháp SAT Cardinality Encoding trên dataset:
python main.py --benchmark-dataset-encodings

# 5. Lọc theo nguồn dữ liệu (chỉ KaggleHub hoặc chỉ Hugging Face):
python main.py --benchmark-dataset --source kaggle --limit 10
python main.py --benchmark-dataset --source huggingface --limit 10

# 6. Lọc theo cấp độ khó (easy, medium, hard, expert):
python main.py --benchmark-dataset --difficulty expert
```

### 4.4. Giải Sudoku & Benchmark ma trận đơn lẻ
```bash
# Giải Sudoku chuẩn 9x9 với phương pháp Product encoding:
python main.py --solve product

# Giải Sudoku kích thước khác (4x4 hoặc 16x16 Hexadoku):
python main.py --size 4 --solve product
python main.py --size 16 --solve product

# Benchmark các Solver trên ma trận mẫu:
python main.py --benchmark-all
python main.py --size 16 --benchmark-all

# Benchmark 5 phương pháp SAT Encoding trên ma trận mẫu:
python main.py --benchmark-sat
python main.py --size 16 --benchmark-sat
```

### 4.5. Chạy hệ thống kiểm thử toàn diện
```bash
# Chạy Unit Tests, Integration Tests cho Solver, Encodings và Dataset Loader:
python main.py --test
```

---

## 5. Sử dụng trong mã nguồn Python

```python
from benchmarks import load_normalized_dataset, benchmark_dataset_solvers
from solvers import solve_sudoku_sat
from utils import print_grid

# 1. Đọc danh sách các bài Sudoku chuẩn hóa từ KaggleHub & Hugging Face:
puzzles = load_normalized_dataset(source="all", difficulty="expert", limit=5)
print(f"Đã đọc {len(puzzles)} bài Sudoku cấp độ Expert")

# 2. Giải puzzle đầu tiên bằng SAT Product:
grid = puzzles[0]["grid"]
solution = solve_sudoku_sat(grid, method="product")
if solution:
    print_grid(solution, f"Nghiệm bài {puzzles[0]['id']}")

# 3. Chạy benchmark so sánh các solver:
benchmark_dataset_solvers(puzzles=puzzles)
```
