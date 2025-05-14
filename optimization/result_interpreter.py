from optimization.tabu_search import Iteration
from typing import List
import numpy as np

class ResultInterpreter:
    def __init__(self, iterations: List[Iteration]):
        self.iterations = iterations

    def store(self):
        numeric_grids: List[List[List[int]]] = []
        for it in self.iterations:
            grid = it.grid.grid
            numeric_grid: List[List[int]] = []
            for row in grid:
                numeric_row: List[int] = []
                for cell in row:
                    if cell.is_entrance:
                        numeric_row.append(-1)
                    elif cell.is_exit:
                        numeric_row.append(-2)
                    else:
                        numeric_row.append(cell.aisle_id)
                numeric_grid.append(numeric_row)
            numeric_grids.append(numeric_grid)
        grid_array = np.array(numeric_grids)

        scores_dtype = np.dtype([
            ('total_score', np.float64),
            ('adjusted_purchases', np.float64),
            ('adjusted_steps', np.float64)
        ])
        scores = np.array(
            [(iter.score.total_score, iter.score.adjusted_purchases, iter.score.adjusted_steps) for iter in self.iterations],
            dtype=scores_dtype
        )

        it_seq = np.array([it.iteration_num for it in self.iterations], dtype=np.int32)


        np.savez("/optimization/results/results.npz", grids=grid_array, scores=scores, it_seq=it_seq)