# Sudoku Solver & SAT Cardinality Encodings (AMO / ALO Framework)

Dự án triển khai và benchmark các thuật toán giải Sudoku 9x9 với trọng tâm là **các kỹ thuật mã hóa SAT cho ràng buộc số lượng (Cardinality Constraints: At-Most-One - AMO, At-Least-One - ALO, Exactly-One - EO)**, đồng thời so sánh hiệu năng với các phương pháp giải tối ưu khác như Constraint Programming (CP) và Integer Linear Programming (ILP/MIP).

---

## 1. Cấu trúc dự án chuẩn mực & logic

```text
Sudoku_prj/
├── sat_encodings/               # Các phương pháp mã hóa SAT cho ALO, AMO, EO
│   ├── __init__.py              # Public API
│   ├── alo.py                   # At-Least-One: (x1 v x2 v ... v xn)
│   ├── pairwise.py              # Pairwise AMO (Naive O(n^2))
│   ├── binary.py                # Binary / Bitwise AMO qua PySAT (Frisch et al., 2005)
│   ├── commander.py             # Commander AMO (Klieber & Kwon, 2007)
│   ├── product.py               # 2-Product AMO (Jingchao Chen, 2010)
│   ├── seqcounter.py            # Sequential Counter AMO qua PySAT (Sinz, 2005)
│   └── manager.py               # Bộ điều phối (Dispatcher: at_most_one, exactly_one)
│
├── solvers/                     # Các bộ giải Sudoku đa phương pháp
│   ├── __init__.py              # Public solver API
│   ├── sat_solver.py            # SAT Solver (Glucose3) hỗ trợ chuyển đổi đa dạng encodings
│   ├── cpsat_solver.py          # Google OR-Tools CP-SAT Solver
│   ├── ilp_solver.py            # PuLP / CBC ILP Solver
│   ├── gurobi_solver.py         # Gurobi Optimizer (MIP)
│   ├── cplex_cp_solver.py       # IBM CPLEX CP Optimizer
│   └── cplex_mip_solver.py      # IBM CPLEX MIP Solver
│
├── benchmarks/                  # Scripts đo lường hiệu năng
│   ├── __init__.py
│   ├── benchmark_solvers.py     # So sánh tất cả các Solver
│   └── benchmark_encodings.py   # So sánh 5 phương pháp SAT Encoding
│
├── tests/                       # Hệ thống kiểm thử tự động
│   ├── __init__.py
│   ├── test_encodings.py        # Kiểm thử tính đúng đắn chân trị (Soundness & Completeness)
│   └── test_solvers.py          # Kiểm thử tích hợp kiểm tra nghiệm các solver
│
├── utils.py                     # Đề bài mẫu (DEFAULT_GRID) & hiển thị bảng Sudoku
├── main.py                      # Điểm vào dòng lệnh (CLI Application)
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn
```

---

## 2. Bảng so sánh các phương pháp mã hóa AMO

| Phương pháp AMO | Thư viện / Tác giả | Biến phụ | Số Clauses | Ưu điểm & Nhược điểm |
| :--- | :--- | :--- | :--- | :--- |
| **Pairwise (Naive)** | Tổ hợp $\binom{n}{2}$ | $0$ | $O(n^2)$ | Dễ cài đặt, không biến phụ, nhưng bùng nổ clause khi $n$ lớn. |
| **Binary (Bitwise)** | PySAT (`EncType.bitwise`) | $\lceil \log_2 n \rceil$ | $O(n \log n)$ | Rất ít biến phụ, số clause tăng theo logarit. |
| **Commander** | Klieber & Kwon (2007) | $O(n/k)$ | $O(n)$ | Tuyến tính cả biến và mệnh đề, chia cụm $k \le 3$ trực quan. |
| **Product (2-Product)**| Jingchao Chen (2010) | $2\lceil\sqrt{n}\rceil$ | $O(n)$ | Mã hóa cực nhanh $O(1)$, cấu trúc lưới 2 chiều thanh lịch. |
| **Sequential Counter**| PySAT (`EncType.seqcounter`) | $n - 1$ | $O(n)$ ($\sim 3n-4$) | Tối ưu hóa lan truyền đơn vị (unit propagation) của SAT solver. |

---

## 3. Hướng dẫn sử dụng

### 3.1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3.2. Chạy ứng dụng qua CLI (`main.py`)
```bash
# 1. Giải Sudoku với phương pháp SAT chỉ định:
python main.py --solve product
python main.py --solve commander
python main.py --solve seqcounter
python main.py --solve binary
python main.py --solve pairwise

# 2. Chạy benchmark so sánh 5 phương pháp mã hóa SAT:
python main.py --benchmark-sat

# 3. Chạy benchmark so sánh tất cả các Solver (SAT, CP-SAT, ILP, CPLEX, Gurobi):
python main.py --benchmark-all

# 4. Chạy toàn bộ hệ thống Unit Tests:
python main.py --test
```

### 3.3. Sử dụng thư viện trong code Python
```python
from sat_encodings import exactly_one, amo_commander, amo_product
from solvers import solve_sudoku_sat

# Sinh mệnh đề AMO cho danh sách biến:
clauses, top_id = amo_commander(lits=[1, 2, 3, 4, 5, 6, 7, 8, 9], top_id=9)

# Giải Sudoku bằng SAT với phương pháp mã hóa tùy chọn:
grid_solution = solve_sudoku_sat(grid=my_sudoku_grid, method="product")
```
