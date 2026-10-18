# Sudoku Solver & SAT Cardinality Encodings (AMO / ALO Framework)

Dự án triển khai và benchmark các thuật toán giải Sudoku tổng quát $N \times N$ (4x4, 9x9, 16x16,...) với trọng tâm là **các kỹ thuật mã hóa SAT cho ràng buộc số lượng (Cardinality Constraints: At-Most-One - AMO, At-Least-One - ALO, Exactly-One - EO)**, đồng thời so sánh hiệu năng với các phương pháp giải tối ưu khác như Constraint Programming (CP) và Integer Linear Programming (ILP/MIP).

Dự án tích hợp trực tiếp **299 bài Sudoku đa kích thước ($4\times4, 9\times9, 16\times16$) và đa dạng cấp độ khó (Easy, Medium, Hard, Expert)** tổng hợp từ **Peter Norvig Benchmark** và **Sudoku Exchange Puzzle Bank** (loader còn hỗ trợ thêm nguồn **KaggleHub** và **Hugging Face** khi có kết nối Internet), đi kèm hệ thống tự động chuẩn hóa dữ liệu thống nhất (Data Normalization Pipeline) và công cụ trực quan hóa Matplotlib phục vụ báo cáo khoa học.

---

## 1. Cấu trúc dự án chuẩn mực & logic

```text
Sudoku_prj/
├── data/                         # Thư mục chứa dữ liệu chuẩn hóa (299 puzzles)
│   └── benchmark_dataset.json   # Dataset benchmark: 279 bài 9x9 + 10 bài 4x4 + 10 bài 16x16
│
├── sat_encodings/               # Các phương pháp mã hóa SAT cho ALO, AMO, EO (generic cho mọi N)
│   ├── __init__.py              # Public API
│   ├── alo.py                   # At-Least-One: (x1 v x2 v ... v xn)
│   ├── pairwise.py              # Pairwise AMO (Naive O(n^2) - Tự cài đặt)
│   ├── binary.py                # Binary / Bitwise AMO qua PySAT (Frisch et al., 2008)
│   ├── commander.py             # Commander AMO (Klieber & Kwon, 2007 - Tự cài đặt)
│   ├── product.py               # 2-Product AMO (Jingchao Chen, 2010 - Tự cài đặt)
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
├── benchmarks/                  # Scripts đo lường hiệu năng & Trực quan hóa
│   ├── __init__.py              # Public benchmark & loader API
│   ├── dataset_loader.py        # Tải, chuẩn hóa và phân loại độ khó theo mật độ clues
│   ├── plotter.py               # Module vẽ biểu đồ Matplotlib (so sánh solvers, encodings, độ khó)
│   ├── benchmark_dataset.py     # Benchmark Solvers & Encodings trên Dataset chuẩn hóa
│   ├── benchmark_solvers.py     # So sánh tất cả các Solver trên ma trận mẫu
│   └── benchmark_encodings.py   # So sánh 5 phương pháp SAT Encoding trên ma trận mẫu
│
├── reports/                     # Thư mục lưu kết quả thực nghiệm (.png, .csv, .json)
├── report/                      # Báo cáo LaTeX (main.tex → main.pdf) & hình minh họa thực nghiệm
├── tests/                       # Hệ thống kiểm thử tự động
│   ├── __init__.py
│   ├── test_encodings.py        # Kiểm thử tính đúng đắn chân trị (Soundness & Completeness)
│   ├── test_solvers.py          # Kiểm thử tích hợp nghiệm các solver trên 4x4, 9x9, 16x16
│   └── test_dataset.py          # Kiểm thử loader & chuẩn hóa dữ liệu đa định dạng
│
├── utils.py                     # Đề bài mẫu (4x4, 9x9, 16x16) & in kẻ khung bàn cờ NxN
├── main.py                      # Điểm vào dòng lệnh (CLI Application hoàn chỉnh)
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn sử dụng
```

---

## 2. Dữ liệu Benchmark (299 Puzzles đa kích thước & độ khó)

### 2.1. Nguồn dữ liệu tích hợp
Loader (`benchmarks/dataset_loader.py`) hỗ trợ 5 nhóm nguồn:
1. **Peter Norvig Benchmark** (tải trực tiếp từ `norvig.com`):
   - `top95`: bộ Sudoku kinh điển và thách thức nhất.
   - `easy50`: bộ chuẩn cơ bản.
   - `hardest`: tuyển tập các bài thách thức bộ giải SAT/Search.
2. **Sudoku Exchange Puzzle Bank**:
   - Ngân hàng câu đố phân loại theo 4 mức: `easy`, `medium`, `hard`, `diabolical` (→ Expert).
3. **KaggleHub** (tùy chọn, cần Internet): `gaz3ll3/top95-sudoku`, `bryanpark/sudoku`.
4. **Hugging Face** (tùy chọn, cần Internet): `Ritvik19/Sudoku-Dataset`, `Alignment-Lab-AI/Expert-Sudoku-100k`, `MathMindsAGI/sudoku_v1`.
5. **Bộ câu đố đa kích thước (Multisize)**:
   - $4 \times 4$ (Mini-Sudoku): 10 bài.
   - $16 \times 16$ (Hexadoku): 10 bài với clue density (mật độ ô gợi ý) từ 18% đến 55%.

### 2.2. Thành phần thực tế của `data/benchmark_dataset.json`
299 bài, phân bố theo kích thước: **279 bài $9\times9$**, **10 bài $4\times4$**, **10 bài $16\times16$**.

| Nguồn (`dataset`) | Số bài |
| :--- | ---: |
| `norvig/top95` | 70 |
| `norvig/easy50` | 50 |
| `norvig/hardest` | 11 |
| `sudoku_exchange/easy` | 43 |
| `sudoku_exchange/medium` | 35 |
| `sudoku_exchange/hard` | 35 |
| `sudoku_exchange/diabolical` | 35 |
| `synthetic_4x4` | 10 |
| `synthetic_16x16` | 10 |
| **Tổng** | **299** |

> Ghi chú: `--source kaggle` / `--source huggingface` chỉ trả về kết quả khi máy có Internet và đã cài `kagglehub` / `datasets`. Nếu tải thất bại, loader tự động dùng các nguồn Norvig + Sudoku Exchange và bộ multisize ở trên.

### 2.3. Chuẩn hóa dữ liệu (Schema thống nhất)
Toàn bộ câu đố từ các nguồn được ánh xạ về một cấu trúc thống nhất:
```json
{
  "id": "exchange_medium_0001",
  "source": "sudoku_exchange",
  "dataset": "sudoku_exchange/medium",
  "size": 9,
  "difficulty": "medium",
  "clues_count": 29,
  "puzzle_string": "020900000048000031000063020009407003003080200400105600030570000250000180000006050",
  "grid": [[0, 2, 0, ...], ...],
  "solution_string": null,
  "solution_grid": null
}
```

Phân loại cấp độ khó dựa trên tỷ lệ mật độ ô gợi ý (Clue Density $\rho = \frac{\text{clues}}{N^2}$), tương ứng với hàm `infer_difficulty()`:
- **Expert**: $\rho \le 27\%$ (với $9\times9$ là $\le 21$ clues).
- **Hard**: $27\% < \rho \le 33\%$ (với $9\times9$ là $22 - 26$ clues).
- **Medium**: $33\% < \rho \le 42\%$ (với $9\times9$ là $27 - 34$ clues).
- **Easy**: $\rho > 42\%$ (với $9\times9$ là $\ge 35$ clues).

Nếu câu đố đã có nhãn độ khó gốc từ nguồn (`diabolical`, `evil` → Expert; `difficult` → Hard; `moderate` → Medium; `simple` → Easy…), nhãn gốc được ưu tiên áp dụng.

---

## 3. Bảng so sánh các phương pháp mã hóa AMO

| Phương pháp AMO | Cách triển khai | Biến phụ | Số Clauses | Đặc tính lý thuyết |
| :--- | :--- | :---: | :---: | :--- |
| **Pairwise (Naive)** | Tự cài đặt (`combinations`) | $0$ | $O(n^2)$ | Dễ cài đặt, không biến phụ, nhưng bùng nổ clause khi $n$ lớn. |
| **Binary (Bitwise)** | PySAT (`EncType.bitwise`, Frisch et al., 2008) | $\lceil \log_2 n \rceil$ | $O(n \log n)$ | Tiết kiệm biến phụ, số clause tăng theo $O(n\log n)$. |
| **Commander** | Tự cài đặt (Klieber & Kwon, 2007), $k=3$ | $O(n/k)$ | $O(n)$ | Tuyến tính cả biến và mệnh đề, chia cụm $k=3$ trực quan. |
| **Product (2-Product)**| Tự cài đặt (Jingchao Chen, 2010) | $2\lceil\sqrt{n}\rceil$ | $O(n)$ | Sinh mệnh đề tuyến tính theo $n$, cấu trúc lưới 2D thanh lịch. |
| **Sequential Counter**| PySAT (`EncType.seqcounter`, Sinz, 2005) | $n - 1$ | $O(n)$ ($3n-4$) | Tối ưu hóa lan truyền đơn vị (unit propagation) của SAT solver. |

---

## 4. Hướng dẫn sử dụng CLI (`main.py`)

### 4.1. Cài đặt thư viện
Yêu cầu **Python ≥ 3.10** (đã kiểm thử trên Python 3.14, Windows x64).

```bash
pip install -r requirements.txt
```

Các bộ giải thương mại (Gurobi, IBM CPLEX) cần **license** khi giải. Nếu thiếu license, lời gọi solver tương ứng chỉ báo lỗi và được ghi nhận là thất bại (chương trình không dừng).

### 4.2. Khởi tạo/Cập nhật Dataset
```bash
# Tải và cập nhật 299 bài Sudoku chuẩn hóa lưu vào data/benchmark_dataset.json:
python main.py --prepare-data
```

### 4.3. Chạy Benchmark trên Dataset chuẩn hóa & Xuất biểu đồ

#### 1. Benchmark 5 phương pháp SAT Encoding (vẽ biểu đồ + timestamp chống trùng file):
```bash
python main.py --benchmark-dataset-encodings --limit 60 --plot --timestamp
```
*Lệnh này sinh ra:*
- `reports/benchmark_encodings_<timestamp>.png`: Biểu đồ cột so sánh thời gian Encode/Solve và quy mô biến/mệnh đề.
- `reports/benchmark_encodings_difficulty_<timestamp>.png`: Biểu đồ đường phân tích xu hướng thời gian qua 4 cấp độ khó (Easy $\to$ Expert).

#### 2. Benchmark các Solver (SAT, CP-SAT, ILP, Gurobi, CPLEX):
```bash
python main.py --benchmark-dataset-solvers --limit 40 --plot --timestamp
```
*Lệnh này sinh ra:*
- `reports/benchmark_solvers_<timestamp>.png`: Biểu đồ so sánh thời gian giải trung bình giữa các công cụ giải chính xác.

#### 3. Benchmark toàn diện (cả Solvers và Encodings):
```bash
python main.py --benchmark-dataset --limit 50 --plot --timestamp
```

#### 4. Lọc theo kích thước ma trận ($N \times N$):
```bash
# Chạy trên bảng 16x16 Hexadoku:
python main.py --benchmark-dataset-encodings --size 16 --plot --timestamp

# Chạy trên bảng 4x4 Mini-Sudoku:
python main.py --benchmark-dataset-encodings --size 4 --plot --timestamp
```

#### 5. Lọc theo nguồn dữ liệu hoặc cấp độ khó cụ thể:
```bash
python main.py --benchmark-dataset --difficulty expert --limit 20
python main.py --benchmark-dataset --source norvig --limit 30
```

#### 6. Xuất dữ liệu thống kê ra file CSV / JSON chi tiết & đặt tên biểu đồ tùy chỉnh:
```bash
python main.py --benchmark-dataset --limit 50 --output-csv reports/results.csv --output-json reports/summary.json

# Đặt tên/đường dẫn biểu đồ tùy chỉnh (tự bật chế độ vẽ):
python main.py --benchmark-dataset-encodings --limit 50 --output-plot reports/my_plot.png
```

---

### 4.4. Giải Sudoku đơn lẻ & Benchmark nhanh
```bash
# Giải bảng mẫu 9x9 bằng SAT (Product encoding):
python main.py --solve product

# Giải bảng kích thước khác (4x4 hoặc 16x16):
python main.py --size 4 --solve product
python main.py --size 16 --solve product

# Benchmark nhanh các solver trên 01 bảng mẫu duy nhất:
python main.py --benchmark-all
python main.py --size 16 --benchmark-all

# Benchmark nhanh 5 phương pháp SAT Encoding trên 01 bảng mẫu duy nhất:
python main.py --benchmark-sat
```

---

### 4.5. Chạy hệ thống kiểm thử tự động
```bash
# Chạy Unit Tests và Integration Tests toàn diện:
python main.py --test
```

---

## 5. Sử dụng trong mã nguồn Python

```python
from benchmarks import load_normalized_dataset, benchmark_dataset_solvers
from solvers import solve_sudoku_sat
from utils import print_grid

# 1. Đọc danh sách các bài Sudoku theo kích thước và độ khó:
puzzles = load_normalized_dataset(size=9, difficulty="expert", limit=5)
print(f"Đã nạp {len(puzzles)} bài Sudoku 9x9 Expert")

# 2. Giải puzzle đầu tiên bằng SAT (phương pháp Product):
grid = puzzles[0]["grid"]
solution = solve_sudoku_sat(grid, method="product")
if solution:
    print_grid(solution, f"Nghiệm bài {puzzles[0]['id']}")

# 3. Chạy benchmark so sánh các solver:
benchmark_dataset_solvers(puzzles=puzzles, plot=True)
```

---

## 6. Tính sẵn sàng của dữ liệu & mã nguồn (Data Availability)

Toàn bộ mã nguồn, các thuật toán mã hóa, dữ liệu benchmark chuẩn hóa và các hình ảnh kết quả thực nghiệm được công khai tại GitHub:
- **Repository URL**: [https://github.com/nmson8206/Sudoku_prj](https://github.com/nmson8206/Sudoku_prj)
