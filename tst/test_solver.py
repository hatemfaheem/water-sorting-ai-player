from unittest import TestCase

from src.solver.solver import Solver, Solution


class TestSolver(TestCase):
    def test_solve_level_103(self):
        level_103 = [
            [0, 1, 2, 3],
            [0, 4, 1, 5],
            [6, 3, 7, 8],
            [1, 0, 7, 9],
            [5, 10, 8, 1],
            [11, 5, 11, 4],
            [11, 8, 6, 7],
            [6, 10, 8, 11],
            [9, 10, 3, 9],
            [2, 3, 4, 0],
            [5, 9, 6, 7],
            [10, 2, 4, 2],
            [],
            [],
        ]

        solver = Solver(debug_mode=False)
        solution: Solution = solver.solve_level(level_103)
        print("\n")
        print(solution)
