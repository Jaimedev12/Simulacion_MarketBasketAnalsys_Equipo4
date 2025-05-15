from dataclasses import dataclass
from optimization.tabu_search import Iteration, TabuSearchScore
from core.grid import SupermarketGrid, GridInput, CellInfo
from typing import List, Tuple
import numpy as np
import os
import shutil


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
        walk_heat_map_array = np.array([it.walk_heat_map for it in self.iterations], dtype=np.float64)
        impulse_heat_map_array = np.array([it.impulse_heat_map for it in self.iterations], dtype=np.float64)

        np.savez(
            directory+"/results.npz", 
            grids=grid_array, 
            scores=scores, 
            it_seq=it_seq, 
            walk_heat_maps=walk_heat_map_array, 
            impulse_heat_maps=impulse_heat_map_array
            )

    def _get_grid_object(self, numeric_grid: List[List[int]]) -> SupermarketGrid:
        # Convert the numeric grid back to a SupermarketGrid object
        rows = len(numeric_grid)
        cols = len(numeric_grid[0]) if rows > 0 else 0
        grid_cells: List[List[CellInfo]] = [[CellInfo(is_walkable=True, aisle_id=0, product_id_range=(0, 0)) for _ in range(cols)] for _ in range(rows)]
        entrance_coords: Tuple[int, int] = (0, 0)
        exit_coords: Tuple[int, int] = (0, 0)

        for x in range(rows):
            for y in range(cols):
                value = numeric_grid[x][y]
                if value == -1:
                    grid_cells[x][y].is_entrance = True
                    entrance_coords = (x, y)
                elif value == -2:
                    grid_cells[x][y].is_exit = True
                    exit_coords = (x, y)
                else:
                    grid_cells[x][y].aisle_id = value
        
        grid_input = GridInput(
            rows=rows,
            cols=cols,
            grid=numeric_grid,
            entrance=entrance_coords,
            exit=exit_coords
        )
        new_grid = SupermarketGrid.from_dict(grid_input)

        return new_grid

    def read_results(self, directory: str = "optimization/results") -> List[Iteration]:
        # Load the results from the .npz file
        data = np.load(directory+"/results.npz")
        grids = data['grids']
        scores = data['scores']
        it_seq = data['it_seq']
        walk_heat_maps = data['walk_heat_maps']
        impulse_heat_maps = data['impulse_heat_maps']
        iterations: List[Iteration] = []

        for i in range(len(grids)):
            it_num: int = it_seq[i]
            score = TabuSearchScore(
                total_score=scores[i][0],
                adjusted_purchases=scores[i][1],
                adjusted_steps=scores[i][2]
            )
            grid = self._get_grid_object(grids[i])

            iteration = Iteration(
                iteration_num=it_num, 
                grid=grid, 
                score=score, 
                walk_heat_map=walk_heat_maps[i],
                impulse_heat_map=impulse_heat_maps[i]
                )
            iterations.append(iteration)

        return iterations
