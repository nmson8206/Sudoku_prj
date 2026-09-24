# This is a sample Python script.
from itertools import combinations
from math import remainder

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from pysat.solvers import Glucose3
from pysat.formula import CNF


grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

def var(r, c, d):
        return 81*r + 9*c + d
def cell_variables(r, c)-> list[int]:
        return [var(r, c, d) for d in range(1,10)]
def row_variables(r, d)-> list[int]:
        return [var(r, c, d) for c in range(9)]
def column_variables(c, d)-> list[int]:
        return [var(r, c, d) for r in range(9)]
def block_variables(r, c, d) -> list[int]:
        return [var(br, bc, d)
                for br in range(r * 3, r * 3 + 3)
                for bc in range(c * 3, c * 3 + 3)]

def at_least_one(vars)-> list[int]:
        return [vars]
def at_most_one(vars)-> list[int]:
        return [[-u, -v] for u, v in combinations(vars, 2)]
def exactly_one(vars)-> list[int]:
        return at_least_one(vars) + at_most_one(vars)
def encode_cell_constraints()-> list[int]:
        clauses = []
        for r in range(9):
                for c in range(9):
                        vars = cell_variables(r, c)
                        clauses += exactly_one(vars)
        return clauses
def encode_block_constraints()-> list[int]:
        clauses = []
        for r in range(3):
                for c in range(3):
                        for d in range(1, 10):
                                vars = block_variables(r, c, d)
                                clauses += exactly_one(vars)
        return clauses
def encode_row_constraints()-> list[int]:
        clauses = []
        for r in range(9):
                for d in range(1, 10):
                        vars = row_variables(r, d)
                        clauses += exactly_one(vars)
        return clauses
def encode_column_constraints()-> list[int]:
        clauses = []
        for c in range(9):
                for d in range(1, 10):
                        vars = column_variables(c, d)
                        clauses += exactly_one(vars)
        return clauses
def encode_clues(grid)-> list[int]:
        clauses = []
        for r in range(9):
                for c in range(9):
                        d = grid[r][c]
                        if (d != 0):
                                clauses.append([var(r, c, d)])
        return clauses

def encode_sudoku(grid)-> list[int]:
        clauses = []
        clauses += encode_row_constraints()
        clauses += encode_column_constraints()
        clauses += encode_block_constraints()
        clauses += encode_cell_constraints()
        clauses += encode_clues(grid)
        return clauses
def sudoku_solve(grid):
        clauses = encode_sudoku(grid)
        solver = Glucose3()
        for clause in clauses:
                solver.add_clause(clause)

        if solver.solve():
                model = solver.get_model()
                return model
        return None

def decode_model(model):
        grid = [[0 for _ in range(9)] for _ in range(9)]
        for x in model:
                if x > 0:
                        x -= 1

                        r = x // 81
                        remainder = x % 81

                        c = remainder // 9
                        d = remainder % 9 + 1

                        grid[r][c] = d
        return grid

if __name__ == "__main__":
        model = sudoku_solve(grid)
        if model:
                solution = decode_model(model)
                for r in solution:
                        print(r)
        else:
                print("No solution")
