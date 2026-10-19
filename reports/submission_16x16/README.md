# Thực nghiệm so sánh solver trên Sudoku 16×16

## Phạm vi

Kết quả của một lượt chạy trên toàn bộ 10 đề `16×16` trong `data/benchmark_dataset.json`, với 10 cấu hình solver. Có 100 bản ghi: 80 nghiệm hợp lệ và 20 lỗi do giới hạn license của Gurobi/CPLEX MIP. Không có kết quả chứng minh vô nghiệm trong lượt chạy này.

- Mã nguồn tại commit: `06a6864aaed024109dd466fd819bc70b869d474a`.
- Thời điểm hoàn tất xuất kết quả (giờ địa phương, theo tệp gốc): 2026-10-19 11:41:35, UTC+07:00.
- CPU Intel Core i5-1235U, 10 nhân vật lý/12 luồng logic, khoảng 16 GB RAM.
- Windows 11, Python 3.14.5; phiên bản gói và SHA-256 dataset nằm trong `environment.json`.

## Tệp kết quả

| Tệp | Nội dung |
| --- | --- |
| `solvers.csv` | 100 bản ghi từng đề–solver, gồm thời gian, trạng thái nghiệm và thông báo lỗi |
| `solvers.json` | Thống kê tổng hợp và toàn bộ bản ghi chi tiết |
| `environment.json` | Commit mã nguồn, phiên bản môi trường, checksum dataset, danh sách đề và giao thức đo |

CSV/JSON kết quả được chép nguyên từ lần chạy trong thư mục tạm; không chỉnh sửa số liệu. Trường `summary` trong JSON chỉ có tám cấu hình có mẫu thời gian; Gurobi và CPLEX MIP vẫn được ghi đầy đủ trong `details` và CSV.

## Kết quả tổng hợp

Thời gian tính bằng mili-giây, làm tròn hai chữ số. Min/max là giá trị giữa **10 đề khác nhau**, không phải độ phân tán qua các lần đo lặp cùng một đề.

| Cấu hình | TB (ms) | Min (ms) | Max (ms) | Nghiệm hợp lệ | Lỗi license |
| --- | ---: | ---: | ---: | ---: | ---: |
| SAT Pairwise | 108.17 | 66.17 | 159.95 | 10/10 | 0 |
| SAT Binary | 77.05 | 43.63 | 115.79 | 10/10 | 0 |
| SAT Commander | 56.79 | 35.61 | 111.68 | 10/10 | 0 |
| SAT Product | 52.85 | 27.95 | 122.33 | 10/10 | 0 |
| SAT Sequential Counter | 65.02 | 36.69 | 111.30 | 10/10 | 0 |
| OR-Tools CP-SAT | 139.57 | 21.66 | 276.75 | 10/10 | 0 |
| PuLP/CBC | 934.46 | 235.95 | 1434.56 | 10/10 | 0 |
| Gurobi MIP | N/A | N/A | N/A | N/A | 10/10 |
| CPLEX CP Optimizer | 61.24 | 42.43 | 98.52 | 10/10 | 0 |
| CPLEX MIP | N/A | N/A | N/A | N/A | 10/10 |

Gurobi báo `Model too large for size-limited license`. CPLEX MIP báo bản promotional giới hạn 1.000 biến/1.000 ràng buộc, trong khi mô hình có 4.096 biến và vượt giới hạn ràng buộc. Các trường hợp này không phải kết quả solver tìm sai nghiệm hoặc xác định đề vô nghiệm.

## Chạy lại

Từ thư mục gốc dự án, với các phụ thuộc và quyền sử dụng solver phù hợp:

```bash
python main.py --benchmark-dataset-solvers --size 16 --output-csv reports/submission_16x16/rerun.csv --output-json reports/submission_16x16/rerun.json
```

Lệnh ghi vào tên `rerun` để không ghi đè kết quả đóng gói. Nên dùng tên mới cho mỗi lần chạy và lưu lại môi trường. Không cần `--prepare-data`: tải lại nguồn động sẽ thay đổi snapshot. Đối chiếu SHA-256 trong `environment.json` trước khi so sánh.

## Cách diễn giải

- Mỗi cặp đề–solver chỉ được đo một lần, theo thứ tự cố định; chưa warm-up, đảo thứ tự hay ước lượng khoảng tin cậy.
- Đo toàn bộ hàm giải: dựng mô hình, gọi bộ giải và giải mã; bước kiểm tra nghiệm nằm ngoài timer.
- Luồng, seed và timeout chưa được chuẩn hóa chung giữa các solver. Thời gian chạy lại có thể khác.
- Nghiệm được kiểm tra theo hàng, cột, khối và gợi ý; không kiểm tra tính duy nhất.
- Đây là dữ liệu tự sinh, không đại diện cho mọi Sudoku kích thước lớn. Kết quả này bổ sung cho báo cáo, không xác minh lại các thời gian 9×9 hoặc giao thức case study cũ.
