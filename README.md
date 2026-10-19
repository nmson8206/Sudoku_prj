# Sudoku Solver & SAT Cardinality Encodings (AMO / ALO Framework)

Dự án mô hình hóa và giải Sudoku bằng SAT, với trọng tâm là các kỹ thuật mã hóa ràng buộc số lượng: **At-Most-One (AMO), At-Least-One (ALO) và Exactly-One (EO)**. Glucose3 được so sánh với các bộ giải CP và ILP/MIP: OR-Tools CP-SAT, IBM CP Optimizer, Gurobi, CPLEX MIP và PuLP/CBC.

Snapshot đóng gói gồm **299 bản ghi, tương ứng 298 đề phân biệt**: 279 bản ghi $9\times9$, 10 đề $4\times4$ và 10 đề $16\times16$. Dữ liệu gồm nguồn **Peter Norvig**, **Sudoku Exchange** và các đề **tự sinh**. Loader còn hỗ trợ KaggleHub/Hugging Face, nhưng snapshot hiện tại không có bản ghi từ hai nguồn này.

- [Báo cáo PDF](report/main.pdf)
- [Mã nguồn báo cáo LaTeX](report/main.tex)

---

## 1. Cấu trúc dự án

```text
Sudoku_prj/
├── data/                         # Snapshot dữ liệu chuẩn hóa
│   └── benchmark_dataset.json   # 299 bản ghi: 279 bài 9x9 + 10 bài 4x4 + 10 bài 16x16
│
├── sat_encodings/               # Các phương pháp mã hóa ALO, AMO và EO
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
│   ├── dataset_loader.py        # Tải, chuẩn hóa; dùng nhãn nguồn hoặc suy ra theo mật độ gợi ý
│   ├── plotter.py               # Module vẽ biểu đồ Matplotlib (so sánh solvers, encodings, độ khó)
│   ├── benchmark_dataset.py     # Benchmark Solvers & Encodings trên Dataset chuẩn hóa
│   ├── benchmark_solvers.py     # So sánh tất cả các Solver trên ma trận mẫu
│   └── benchmark_encodings.py   # So sánh 5 phương pháp SAT Encoding trên ma trận mẫu
│
├── reports/                     # Biểu đồ và kết quả CSV/JSON, gồm thực nghiệm submission_16x16/
├── report/                      # Báo cáo LaTeX (main.tex → main.pdf) & hình minh họa thực nghiệm
├── tests/                       # Hệ thống kiểm thử tự động
│   ├── __init__.py
│   ├── test_encodings.py        # Kiểm thử tính đúng đắn chân trị (Soundness & Completeness)
│   ├── test_solvers.py          # Kiểm thử tích hợp nghiệm các solver trên 4x4, 9x9, 16x16
│   └── test_dataset.py          # Kiểm thử loader & chuẩn hóa dữ liệu đa định dạng
│
├── utils.py                     # Đề bài mẫu (4x4, 9x9, 16x16) & in kẻ khung bàn cờ NxN
├── main.py                      # Điểm vào giao diện dòng lệnh (CLI)
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn sử dụng
```

---

## 2. Dữ liệu benchmark

### 2.1. Nguồn dữ liệu tích hợp
Loader (`benchmarks/dataset_loader.py`) hỗ trợ 5 nhóm nguồn:
1. **Peter Norvig Benchmark** (tải trực tiếp từ `norvig.com`):
   - `top95`, `easy50`, `hardest`: các tập đề dùng để khảo sát thuật toán giải Sudoku.
2. **Sudoku Exchange Puzzle Bank**:
   - Ngân hàng câu đố phân loại theo 4 mức: `easy`, `medium`, `hard`, `diabolical` (→ Expert).
3. **KaggleHub** (tùy chọn, cần Internet): `gaz3ll3/top95-sudoku`, `bryanpark/sudoku`.
4. **Hugging Face** (tùy chọn, cần Internet): `Ritvik19/Sudoku-Dataset`, `Alignment-Lab-AI/Expert-Sudoku-100k`, `MathMindsAGI/sudoku_v1`.
5. **Dữ liệu đa kích thước tự sinh**:
   - $4\times4$: 10 đề.
   - $16\times16$: 10 đề, xóa ô từ một nghiệm cơ sở với seed 42; tỷ lệ ô giữ lại được cấu hình từ 18% đến 55%. Cách sinh bảo đảm có nghiệm nhưng chưa bảo đảm duy nhất.

### 2.2. Thành phần thực tế của `data/benchmark_dataset.json`
**299 bản ghi**: 279 bản ghi $9\times9$, 10 bản ghi $4\times4$, 10 bản ghi $16\times16$.

| Nguồn (`dataset`) | Số bản ghi |
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


### 2.3. Chuẩn hóa dữ liệu (Schema thống nhất)
Mỗi đề được ánh xạ về schema chung. Ví dụ dưới đây minh họa cấu trúc bằng bảng $4\times4$, không phải một bản ghi trích nguyên văn từ snapshot:
```json
{
  "id": "example_4x4",
  "source": "example",
  "dataset": "example/4x4",
  "size": 4,
  "difficulty": "medium",
  "clues_count": 6,
  "puzzle_string": "1004040001030020",
  "grid": [[1, 0, 0, 4], [0, 4, 0, 0], [0, 1, 0, 3], [0, 0, 2, 0]],
  "solution_string": null,
  "solution_grid": null
}
```

Ô trống được biểu diễn bằng `0`; chuỗi đầu vào có thể dùng `.` cho ô trống và ký hiệu chữ cho giá trị lớn hơn 9. Khi không có nhãn nguồn được nhận diện, `infer_difficulty()` suy ra độ khó từ mật độ gợi ý $\rho=\mathrm{clues}/N^2$:
- **Expert**: $\rho \le 27\%$ (với $9\times9$ là $\le 21$ clues).
- **Hard**: $27\% < \rho \le 33\%$ (với $9\times9$ là $22 - 26$ clues).
- **Medium**: $33\% < \rho \le 42\%$ (với $9\times9$ là $27 - 34$ clues).
- **Easy**: $\rho > 42\%$ (với $9\times9$ là $\ge 35$ clues).

Nếu có nhãn nguồn được nhận diện (`diabolical`, `evil` → Expert; `difficult` → Hard; `moderate` → Medium; `simple` → Easy…), loader ưu tiên nhãn đó. Khi đọc snapshot, nhãn lưu sẵn được giữ nguyên; một số nhãn hiện không khớp quy tắc ưu tiên nguồn của loader. Vì vậy, tải lại có thể thay đổi phân bố nhãn. Số gợi ý và nhãn nguồn không phải thước đo độ khó thống nhất cho mọi solver.

---

## 3. Bảng so sánh các phương pháp mã hóa AMO

| Phương pháp AMO | Cách triển khai | Biến phụ | Số Clauses | Đặc tính lý thuyết |
| :--- | :--- | :---: | :---: | :--- |
| **Pairwise (Naive)** | Tự cài đặt (`combinations`) | $0$ | $O(n^2)$ | Dễ cài đặt, không biến phụ, nhưng bùng nổ clause khi $n$ lớn. |
| **Binary (Bitwise)** | PySAT (`EncType.bitwise`, Frisch et al., 2008) | $\lceil \log_2 n \rceil$ | $O(n \log n)$ | Tiết kiệm biến phụ, số clause tăng theo $O(n\log n)$. |
| **Commander** | Tự cài đặt (Klieber & Kwon, 2007), nhóm $k=3$ | $O(n)$ với $k$ cố định | $O(n)$ | Chia nhóm và mã hóa đệ quy trên biến chỉ huy. |
| **Product (2-Product)** | Tự cài đặt (Jingchao Chen, 2010) | $p+q=O(\sqrt n)$ | $2n+\binom p2+\binom q2=O(n)$ | Lưới $p=\lceil\sqrt n\rceil$, $q=\lceil n/p\rceil$; dùng Pairwise trên biến hàng/cột. |
| **Sequential Counter** | PySAT (`EncType.seqcounter`, Sinz, 2005) | $n-1$ | $3n-4=O(n)$ | Lan truyền qua chuỗi biến đếm. |

Các công thức mô tả một nhóm AMO với $n\ge2$; thư viện có thể rút gọn trường hợp nhỏ. Product chỉ có $p+q=2\sqrt n$ khi $n$ là số chính phương. Với Sudoku, có $4N^2$ nhóm EO và mỗi EO gồm một ALO cùng một AMO, ngoài các mệnh đề đơn nguyên cho gợi ý.

---

## 4. Hướng dẫn sử dụng CLI (`main.py`)

### 4.1. Cài đặt thư viện
Yêu cầu **Python ≥ 3.10**; cấu hình được ghi trong báo cáo là Python 3.14 trên Windows x64. Chạy lệnh từ thư mục gốc dự án. `requirements.txt` chỉ quy định khoảng phiên bản, chưa khóa chính xác môi trường thực nghiệm.

```bash
pip install -r requirements.txt
```

Gurobi và IBM CPLEX cần thư viện cùng license/quyền sử dụng phù hợp. Benchmark trên dataset bắt lỗi trong từng lời gọi solver và ghi nhận thất bại, nhưng thiếu gói thư viện lúc import có thể khiến CLI dừng trước khi benchmark bắt đầu. Không nên coi tất cả phụ thuộc thương mại là tùy chọn có thể bỏ cài đặt. Cần phân biệt lỗi môi trường/license với kết quả không có nghiệm.

### 4.2. Sử dụng hoặc tải lại dữ liệu
Các lệnh benchmark đọc snapshot sẵn có; **không cần chạy `--prepare-data` để dùng dữ liệu đóng gói**.

> **Lưu ý:** lệnh dưới tải lại các nguồn và ghi đè `data/benchmark_dataset.json`. Số lượng đề, nguồn và nhãn phụ thuộc kết nối, dữ liệu trực tuyến và cấu hình loader; không bảo đảm tạo đúng 299 bản ghi. Hãy sao lưu snapshot trước nếu cần giữ nguyên dữ liệu dùng trong báo cáo.

```bash
python main.py --prepare-data
```

### 4.3. Chạy Benchmark trên Dataset chuẩn hóa & Xuất biểu đồ

**Mặc định:** CLI dùng `--size 9`, vì vậy không tự chạy cả 299 bản ghi. Chọn `--size 4` hoặc `--size 16` để khảo sát nhóm khác. `--limit` lấy các bản ghi đầu theo nhóm độ khó (cố gắng phân bổ giữa các nhóm), không phải lấy mẫu ngẫu nhiên; nếu đã lọc một độ khó thì lấy các bản ghi đầu nhóm đó.

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

#### 6. Xuất dữ liệu thống kê ra file CSV / JSON (tự động hoặc tùy chỉnh):
```bash
# Cách 1: Xuất nhanh không cần nhập đường dẫn (tự động lưu vào reports/):
python main.py --benchmark-dataset --limit 50 --csv --json

# Xuất nhanh kết hợp --timestamp để tự động đánh dấu thời gian chống trùng lặp:
python main.py --benchmark-dataset --limit 50 --csv --json --timestamp

# Cách 2: Tùy chỉnh đường dẫn hoặc tên file theo ý muốn:
python main.py --benchmark-dataset --limit 50 --output-csv reports/results.csv --output-json reports/summary.json

# Tùy chỉnh tên file kèm --timestamp:
python main.py --benchmark-dataset --limit 50 --timestamp --output-csv reports/results.csv --output-json reports/summary.json
# Kết quả sinh ra: reports/results_<timestamp>.csv (và _solvers_<timestamp>.csv), reports/summary_<timestamp>.json (và _solvers_<timestamp>.json)

# Đặt tên/đường dẫn biểu đồ tùy chỉnh (tự bật chế độ vẽ):
python main.py --benchmark-dataset-encodings --limit 50 --output-plot reports/my_plot.png
```

---

### 4.4. Giải Sudoku đơn lẻ & Benchmark nhanh
`--solve` giải bảng mẫu của kích thước được chọn, chưa hỗ trợ nhập đề tùy ý qua tệp CLI. Có thể truyền ma trận trực tiếp qua API Python ở Mục 5.

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
# Chạy các bộ kiểm thử hiện có:
python main.py --test
```

Kiểm thử encoding duyệt $2^6$ phép gán ở `n=6` cho ALO, năm AMO và năm EO; chưa bao phủ mọi kích thước hoặc trường hợp rỗng/đơn phần tử. Kiểm thử solver trên $9\times9$ có các bộ giải đã tích hợp, trên $4\times4$ có SAT Product/CP-SAT/CBC, trên $16\times16$ có SAT Product/CP-SAT. Các kiểm thử thương mại có thể bị bỏ qua khi gặp lỗi; cần đọc log từng trường hợp thay vì coi việc kết thúc chương trình là mọi solver đều đạt. Kiểm tra nghiệm xác minh hàng, cột, khối và gợi ý, không chứng minh duy nhất.

---

## 5. Sử dụng trong mã nguồn Python

```python
from benchmarks import load_normalized_dataset, benchmark_dataset_solvers
from solvers import solve_sudoku_sat
from utils import print_grid

# 1. Đọc danh sách các bài Sudoku theo kích thước và độ khó:
puzzles = load_normalized_dataset(size=9, difficulty="expert", limit=5)
print(f"Đã nạp {len(puzzles)} bài Sudoku 9x9 Expert")

# 2. Giải đề đầu tiên bằng SAT (Product), nếu bộ lọc có dữ liệu:
if puzzles:
    grid = puzzles[0]["grid"]
    solution = solve_sudoku_sat(grid, method="product")
    if solution:
        print_grid(solution, f"Nghiệm bài {puzzles[0]['id']}")

# 3. Chạy benchmark so sánh các solver:
benchmark_dataset_solvers(puzzles=puzzles, plot=True)
```

---

## 6. Phạm vi đo và giới hạn tái lập

- **Benchmark encoding:** đo sinh CNF và lời gọi `solver.solve()`. `total_ms` là tổng hai pha, **không gồm** khởi tạo solver, nạp CNF, giải mã hoặc kiểm tra nghiệm.
- **Benchmark solver:** đo toàn bộ hàm giải, gồm dựng mô hình và các chi phí trong wrapper; không tính kiểm tra nghiệm bên ngoài. Vì vậy, thời gian hai loại benchmark không so sánh trực tiếp được.
- Benchmark dataset kiểm tra nghiệm theo luật Sudoku và gợi ý. Hiện đo một lần cho mỗi cặp đề–phương pháp, theo thứ tự cố định; chưa có warm-up, khoảng tin cậy hoặc cấu hình timeout/số luồng/seed thống nhất giữa các solver.
- Các exception được ghi nhận là lỗi và không có thời gian; các bản ghi này bị loại khỏi trung bình. Hãy đọc đồng thời tỷ lệ nghiệm hợp lệ và số lần lỗi, không xếp hạng chỉ bằng thời gian.
- [Thực nghiệm 16×16](reports/submission_16x16/README.md) có CSV/JSON của 100 bản ghi đề–solver, phiên bản môi trường, checksum dataset và lệnh chạy lại. Có 80 nghiệm hợp lệ; 20 lỗi từ Gurobi/CPLEX MIP là giới hạn license, không phải kết quả vô nghiệm. Đây là một lượt đo, chưa có khoảng tin cậy. Dữ liệu mới không xác minh lại thời gian 9×9 hoặc case study cũ. Để lưu lần chạy khác, dùng tên tệp mới hoặc `--csv --json --timestamp`.
- Case study trong báo cáo có thời gian tham khảo đã ghi nhận; repository chưa cung cấp đủ script và dữ liệu thô xác nhận giao thức cực tiểu 60 lần qua ba phiên. Không coi đó là quy trình đã được các script benchmark hiện tại tự động thực hiện.
- Dữ liệu trùng, dữ liệu tự sinh, nhãn không đồng nhất và kiểm tra đầu vào chưa đầy đủ là các giới hạn hiện có. Kết quả không chứng minh ưu thế tổng quát của SAT trước CP/MIP.

## 7. Mã nguồn và báo cáo

- **Repository:** [https://github.com/nmson8206/Sudoku_prj](https://github.com/nmson8206/Sudoku_prj)
- **Báo cáo:** [PDF](report/main.pdf) · [LaTeX](report/main.tex)
- **Snapshot dữ liệu:** [data/benchmark_dataset.json](data/benchmark_dataset.json)
- **Kết quả thô 16×16:** [Hướng dẫn và bảng tổng hợp](reports/submission_16x16/README.md) · [CSV](reports/submission_16x16/solvers.csv) · [JSON](reports/submission_16x16/solvers.json) · [Môi trường](reports/submission_16x16/environment.json)
