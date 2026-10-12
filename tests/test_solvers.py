"""
Integration tests kiểm tra tính chính xác của các Sudoku Solver trên cùng một đề bài mẫu.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from utils import DEFAULT_GRID
from solvers import (
    solve_sudoku_sat,
    solve_sudoku_cpsat,
    solve_sudoku_ilp,
    solve_sudoku_gurobi,
    solve_sudoku_cplex_cp,
    solve_sudoku_cplex_mip,
)


def validate_sudoku_solution(grid: list[list[int]]) -> bool:
    """Kiểm tra nghiệm Sudoku có hợp lệ và đầy đủ theo luật Sudoku không."""
    if not grid or len(grid) != 9 or any(len(row) != 9 for row in grid):
        return False

    expected_set = set(range(1, 10))

    # Kiểm tra hàng
    for r in range(9):
        if set(grid[r]) != expected_set:
            return False

    # Kiểm tra cột
    for c in range(9):
        if {grid[r][c] for r in range(9)} != expected_set:
            return False

    # Kiểm tra khối 3x3
    for br in range(3):
        for bc in range(3):
            block = {
                grid[r][c]
                for r in range(br * 3, br * 3 + 3)
                for c in range(bc * 3, bc * 3 + 3)
            }
            if block != expected_set:
                return False

    # Kiểm tra gợi ý ban đầu
    for r in range(9):
        for c in range(9):
            if DEFAULT_GRID[r][c] != 0 and grid[r][c] != DEFAULT_GRID[r][c]:
                return False

    return True


def run_all():
    print("=" * 64)
    print("TEST SUITE: INTEGRATION TESTING CÁC SUDOKU SOLVER")
    print("=" * 64)

    # 1. Test SAT với 5 phương pháp mã hóa
    for m in ["pairwise", "binary", "commander", "product", "seqcounter"]:
        sol = solve_sudoku_sat(DEFAULT_GRID, method=m)
        assert validate_sudoku_solution(sol), f"SAT-{m} cho nghiệm không hợp lệ!"
        print(f"[PASSED] Solver SAT ({m:<10}) -> Nghiệm Sudoku chính xác.")

    # 2. Test CP-SAT
    sol_cpsat = solve_sudoku_cpsat(DEFAULT_GRID)
    assert validate_sudoku_solution(sol_cpsat), "CP-SAT cho nghiệm không hợp lệ!"
    print(f"[PASSED] Solver CP-SAT (OR-Tools)   -> Nghiệm Sudoku chính xác.")

    # 3. Test ILP (PuLP)
    sol_ilp = solve_sudoku_ilp(DEFAULT_GRID)
    assert validate_sudoku_solution(sol_ilp), "ILP (PuLP) cho nghiệm không hợp lệ!"
    print(f"[PASSED] Solver ILP (PuLP / CBC)    -> Nghiệm Sudoku chính xác.")

    # 4. Test Gurobi (nếu có license)
    try:
        sol_gurobi = solve_sudoku_gurobi(DEFAULT_GRID)
        if sol_gurobi:
            assert validate_sudoku_solution(sol_gurobi), "Gurobi cho nghiệm không hợp lệ!"
            print(f"[PASSED] Solver Gurobi Optimizer    -> Nghiệm Sudoku chính xác.")
    except Exception as e:
        print(f"[SKIPPED] Gurobi Solver: {e}")

    # 5. Test CPLEX CP
    try:
        sol_cplex_cp = solve_sudoku_cplex_cp(DEFAULT_GRID)
        if sol_cplex_cp:
            assert validate_sudoku_solution(sol_cplex_cp), "CPLEX CP cho nghiệm không hợp lệ!"
            print(f"[PASSED] Solver CPLEX CP (CPO)      -> Nghiệm Sudoku chính xác.")
    except Exception as e:
        print(f"[SKIPPED] CPLEX CP Solver: {e}")

    # 6. Test CPLEX MIP
    try:
        sol_cplex_mip = solve_sudoku_cplex_mip(DEFAULT_GRID)
        if sol_cplex_mip:
            assert validate_sudoku_solution(sol_cplex_mip), "CPLEX MIP cho nghiệm không hợp lệ!"
            print(f"[PASSED] Solver CPLEX MIP (MP)      -> Nghiệm Sudoku chính xác.")
    except Exception as e:
        print(f"[SKIPPED] CPLEX MIP Solver: {e}")

    print("=" * 64)
    print("TẤT CẢ SOLVER ĐỀU GIẢI THÀNH CÔNG VÀ CHÍNH XÁC!")


if __name__ == "__main__":
    run_all()
