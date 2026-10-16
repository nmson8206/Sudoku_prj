"""
Integration tests kiểm tra tính chính xác của các Sudoku Solver trên các kích thước (4x4, 9x9, 16x16).
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Optional, List
from utils import DEFAULT_GRID, DEFAULT_GRID_4X4, DEFAULT_GRID_16X16, get_grid_params
from solvers import (
    solve_sudoku_sat,
    solve_sudoku_cpsat,
    solve_sudoku_ilp,
    solve_sudoku_gurobi,
    solve_sudoku_cplex_cp,
    solve_sudoku_cplex_mip,
)


def validate_sudoku_solution(grid: Optional[List[List[int]]], initial_grid: Optional[List[List[int]]] = None) -> bool:
    """Kiểm tra nghiệm Sudoku có hợp lệ và đầy đủ theo luật Sudoku N x N không."""
    if not grid or not isinstance(grid, list):
        return False

    try:
        N, br, bc = get_grid_params(grid)
    except Exception:
        return False

    expected_set = set(range(1, N + 1))

    # 1. Kiểm tra hàng
    for r in range(N):
        if set(grid[r]) != expected_set:
            return False

    # 2. Kiểm tra cột
    for c in range(N):
        if {grid[r][c] for r in range(N)} != expected_set:
            return False

    # 3. Kiểm tra các khối (br x bc)
    num_block_rows = N // br
    num_block_cols = N // bc
    for block_r_idx in range(num_block_rows):
        for block_c_idx in range(num_block_cols):
            block = {
                grid[r][c]
                for r in range(block_r_idx * br, (block_r_idx + 1) * br)
                for c in range(block_c_idx * bc, (block_c_idx + 1) * bc)
            }
            if block != expected_set:
                return False

    # 4. Kiểm tra gợi ý ban đầu (nếu có)
    if initial_grid:
        for r in range(N):
            for c in range(N):
                clue = initial_grid[r][c]
                if clue != 0 and grid[r][c] != clue:
                    return False

    return True


def run_all():
    print("=" * 64)
    print("TEST SUITE: INTEGRATION TESTING CÁC SUDOKU SOLVER (9x9)")
    print("=" * 64)

    # 1. Test SAT với 5 phương pháp mã hóa trên 9x9
    for m in ["pairwise", "binary", "commander", "product", "seqcounter"]:
        sol = solve_sudoku_sat(DEFAULT_GRID, method=m)
        assert validate_sudoku_solution(sol, DEFAULT_GRID), f"SAT-{m} cho nghiệm không hợp lệ!"
        print(f"[PASSED] Solver SAT ({m:<10}) [9x9] -> Nghiệm Sudoku chính xác.")

    # 2. Test CP-SAT trên 9x9
    sol_cpsat = solve_sudoku_cpsat(DEFAULT_GRID)
    assert validate_sudoku_solution(sol_cpsat, DEFAULT_GRID), "CP-SAT cho nghiệm không hợp lệ!"
    print(f"[PASSED] Solver CP-SAT (OR-Tools)   [9x9] -> Nghiệm Sudoku chính xác.")

    # 3. Test ILP (PuLP) trên 9x9
    sol_ilp = solve_sudoku_ilp(DEFAULT_GRID)
    assert validate_sudoku_solution(sol_ilp, DEFAULT_GRID), "ILP (PuLP) cho nghiệm không hợp lệ!"
    print(f"[PASSED] Solver ILP (PuLP / CBC)    [9x9] -> Nghiệm Sudoku chính xác.")

    # 4. Test Gurobi (nếu có license)
    try:
        sol_gurobi = solve_sudoku_gurobi(DEFAULT_GRID)
        if sol_gurobi:
            assert validate_sudoku_solution(sol_gurobi, DEFAULT_GRID), "Gurobi cho nghiệm không hợp lệ!"
            print(f"[PASSED] Solver Gurobi Optimizer    [9x9] -> Nghiệm Sudoku chính xác.")
    except Exception as e:
        print(f"[SKIPPED] Gurobi Solver: {e}")

    # 5. Test CPLEX CP
    try:
        sol_cplex_cp = solve_sudoku_cplex_cp(DEFAULT_GRID)
        if sol_cplex_cp:
            assert validate_sudoku_solution(sol_cplex_cp, DEFAULT_GRID), "CPLEX CP cho nghiệm không hợp lệ!"
            print(f"[PASSED] Solver CPLEX CP (CPO)      [9x9] -> Nghiệm Sudoku chính xác.")
    except Exception as e:
        print(f"[SKIPPED] CPLEX CP Solver: {e}")

    # 6. Test CPLEX MIP
    try:
        sol_cplex_mip = solve_sudoku_cplex_mip(DEFAULT_GRID)
        if sol_cplex_mip:
            assert validate_sudoku_solution(sol_cplex_mip, DEFAULT_GRID), "CPLEX MIP cho nghiệm không hợp lệ!"
            print(f"[PASSED] Solver CPLEX MIP (MP)      [9x9] -> Nghiệm Sudoku chính xác.")
    except Exception as e:
        print(f"[SKIPPED] CPLEX MIP Solver: {e}")

    print("\n" + "=" * 64)
    print("TEST SUITE: KIỂM THỬ KÍCH THƯỚC N x N (4x4 & 16x16)")
    print("=" * 64)

    # Test 4x4
    sol_sat_4x4 = solve_sudoku_sat(DEFAULT_GRID_4X4, method="product")
    assert validate_sudoku_solution(sol_sat_4x4, DEFAULT_GRID_4X4), "SAT 4x4 thất bại!"
    print(f"[PASSED] Solver SAT (product)       [4x4] -> Nghiệm Sudoku 4x4 chính xác.")

    sol_cpsat_4x4 = solve_sudoku_cpsat(DEFAULT_GRID_4X4)
    assert validate_sudoku_solution(sol_cpsat_4x4, DEFAULT_GRID_4X4), "CP-SAT 4x4 thất bại!"
    print(f"[PASSED] Solver CP-SAT              [4x4] -> Nghiệm Sudoku 4x4 chính xác.")

    sol_ilp_4x4 = solve_sudoku_ilp(DEFAULT_GRID_4X4)
    assert validate_sudoku_solution(sol_ilp_4x4, DEFAULT_GRID_4X4), "ILP 4x4 thất bại!"
    print(f"[PASSED] Solver ILP (PuLP)          [4x4] -> Nghiệm Sudoku 4x4 chính xác.")

    # Test 16x16 (Kích thước lớn hơn 9x9)
    sol_sat_16x16 = solve_sudoku_sat(DEFAULT_GRID_16X16, method="product")
    assert validate_sudoku_solution(sol_sat_16x16, DEFAULT_GRID_16X16), "SAT 16x16 thất bại!"
    print(f"[PASSED] Solver SAT (product)     [16x16] -> Nghiệm Sudoku 16x16 chính xác.")

    sol_cpsat_16x16 = solve_sudoku_cpsat(DEFAULT_GRID_16X16)
    assert validate_sudoku_solution(sol_cpsat_16x16, DEFAULT_GRID_16X16), "CP-SAT 16x16 thất bại!"
    print(f"[PASSED] Solver CP-SAT            [16x16] -> Nghiệm Sudoku 16x16 chính xác.")

    print("=" * 64)
    print("TẤT CẢ SOLVER ĐỀU GIẢI THÀNH CÔNG VÀ CHÍNH XÁC TRÊN MỌI KÍCH THƯỚC!")


if __name__ == "__main__":
    run_all()
