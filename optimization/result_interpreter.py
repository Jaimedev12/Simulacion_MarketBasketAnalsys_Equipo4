from dataclasses import dataclass
from optimization.tabu_search import Iteration
from typing import List, Tuple
import numpy as np
import os
import shutil

# @dataclass
# class ResultDataset:


class ResultInterpreter:
    def __init__(self, iterations: List[Iteration]):
        self.iterations = iterations

    def store(self, directory: str = "optimization/results"):
        # Define the results directory
        
        if os.path.exists(directory):
            shutil.rmtree(directory)
            os.makedirs(directory)    
        else:
            # Create directory if it doesn't exist
            os.makedirs(directory)


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

        np.savez(directory+"/results.npz", grids=grid_array, scores=scores, it_seq=it_seq)

    def read_results(self, directory: str = "optimization/results") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Load the results from the .npz file
        data = np.load(directory+"/results.npz")
        grids = data['grids']
        scores = data['scores']
        it_seq = data['it_seq']
        return grids, scores, it_seq
