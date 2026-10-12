"""
Package solvers: Tập hợp các phương pháp giải Sudoku:
- solve_sudoku_sat (SAT Solver - Glucose3, đa dạng encoding)
- solve_sudoku_cpsat (CP-SAT Solver - Google OR-Tools)
- solve_sudoku_ilp (ILP Solver - PuLP / CBC)
- solve_sudoku_gurobi (MIP Solver - Gurobi Optimizer)
- solve_sudoku_cplex_cp (CP Solver - IBM CP Optimizer)
- solve_sudoku_cplex_mip (MIP Solver - IBM CPLEX MIP)
"""

from .sat_solver import solve_sudoku_sat, encode_sudoku, decode_model
from .cpsat_solver import solve_sudoku_cpsat
from .ilp_solver import solve_sudoku_ilp
from .gurobi_solver import solve_sudoku_gurobi
from .cplex_cp_solver import solve_sudoku_cplex_cp
from .cplex_mip_solver import solve_sudoku_cplex_mip

__all__ = [
    "solve_sudoku_sat",
    "encode_sudoku",
    "decode_model",
    "solve_sudoku_cpsat",
    "solve_sudoku_ilp",
    "solve_sudoku_gurobi",
    "solve_sudoku_cplex_cp",
    "solve_sudoku_cplex_mip",
]
