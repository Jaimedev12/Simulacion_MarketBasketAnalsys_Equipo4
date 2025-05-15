from copy import deepcopy
from dataclasses import dataclass

from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from core.grid import SupermarketGrid, CellInfo
from core.customer import CustomerSimulator
from .neighborhood import gen_neighbors
from typing import List, Tuple, Dict
import hashlib
import os
from visualization.visualization import generate_individual_plot

@dataclass
class TabuSearchScore:
    total_score: float
    adjusted_purchases: float
    adjusted_steps: float

HeatMap = List[List[float]]

@dataclass
class Iteration:
    grid: SupermarketGrid
    score: TabuSearchScore
    iteration_num: int
    walk_heat_map: HeatMap
    impulse_heat_map: HeatMap

@dataclass
class EvaluateResult:
    score: TabuSearchScore
    walk_heat_map: HeatMap
    impulse_heat_map: HeatMap

@dataclass
class Neighbor:
    grid: SupermarketGrid
    score: TabuSearchScore
    walk_heat_map: HeatMap
    impulse_heat_map: HeatMap
    is_worth_exploring: bool


class TabuSearchOptimizer:
    def __init__(self, initial_grid: SupermarketGrid, customers: List[CustomerSimulator]):
        self.tabu_list = []
        self.customers: List[CustomerSimulator] = customers
        
        self.current_solution: SupermarketGrid= initial_grid
        curr_eval = self.evaluate_solution(self.current_solution)
        self.current_score: TabuSearchScore = curr_eval.score
        self.current_walk_heat_map: HeatMap = curr_eval.walk_heat_map
        self.current_impulse_heat_map: HeatMap = curr_eval.impulse_heat_map

        self.best_solution: SupermarketGrid = deepcopy(self.current_solution)
        self.best_score: TabuSearchScore = self.current_score
        self.best_walk_heat_map: HeatMap = self.current_walk_heat_map
        self.best_impulse_heat_map: HeatMap = self.current_impulse_heat_map

        self.iterations: List[Iteration] = []
        self.log_iteration(0)
        
    def change_curr_grid(self, new_grid: SupermarketGrid, restart_score: bool = False):
        """Cambia la cuadrícula actual"""
        self.tabu_list = []

        self.current_solution = new_grid

        curr_eval = self.evaluate_solution(self.current_solution)
        self.current_score = curr_eval.score
        self.current_walk_heat_map = curr_eval.walk_heat_map
        self.current_impulse_heat_map = curr_eval.impulse_heat_map
        
        if self.current_score.total_score > self.best_score.total_score:
            restart_score = True
        
        if restart_score:
            self.best_score = self.current_score
            self.best_solution = deepcopy(self.current_solution)
            self.best_walk_heat_map = self.current_walk_heat_map
            self.best_impulse_heat_map = self.current_impulse_heat_map

        self.log_iteration(0)

    def _normalize_heat_map(self, heat_map: HeatMap) -> HeatMap:
        """Normaliza el mapa de calor"""
        max_value = max(max(row) for row in heat_map)
        min_value = min(min(row) for row in heat_map)
        normalized_heat_map = [
            [(cell - min_value) / (max_value - min_value) for cell in row]
            for row in heat_map
        ]
        return normalized_heat_map

    def evaluate_solution(self, solution: SupermarketGrid) -> EvaluateResult:
        """Evalúa una solución con simulaciones de clientes"""
        total_score: float = 0.0
        adjusted_purchases_sum: float = 0.0
        adjusted_steps_sum: float = 0.0
        walk_heat_map: HeatMap = [[0.0 for _ in range(solution.cols)] for _ in range(solution.rows)]
        impulse_heat_map: HeatMap = [[0.0 for _ in range(solution.cols)] for _ in range(solution.rows)]
        for customer in self.customers:
            result = customer.simulate(solution)
            num_products = len(customer.shopping_list)

            adjusted_purchases = result.impulsive_purchases / num_products
            adjusted_steps = len(result.path) / num_products
            total_score += adjusted_purchases - adjusted_steps
            adjusted_purchases_sum += adjusted_purchases
            adjusted_steps_sum += adjusted_steps

            for pos in result.path:
                walk_heat_map[pos[0]][pos[1]] += 1.0
            
            for shelf_pos in result.impulsive_shelfs:
                impulse_heat_map[shelf_pos[0]][shelf_pos[1]] += 1.0

        normalized_walk_heat_map = self._normalize_heat_map(walk_heat_map)
        normalized_impulse_heat_map = self._normalize_heat_map(impulse_heat_map)

        return EvaluateResult(
            TabuSearchScore(
            total_score/len(self.customers), 
            adjusted_purchases_sum/len(self.customers), 
            adjusted_steps=adjusted_steps_sum/len(self.customers)
            ), 
            normalized_walk_heat_map, 
            normalized_impulse_heat_map
            )

    def log_iteration(self, save_it_as: int):
        print(f"Iteration {save_it_as}: Best score: {self.best_score.total_score}")
        print(f"Current score ->", end=" ")
        print(f"Total: {round(self.current_score.total_score, 2)} ", end=" ")
        print(f"Purchases: {round(self.current_score.adjusted_purchases, 2)}", end=" ")
        print(f"Steps: {round(self.current_score.adjusted_steps, 2)}")
        self.iterations.append(
            Iteration(
                self.current_solution, 
                self.current_score, 
                save_it_as, 
                self.current_walk_heat_map,
                self.current_impulse_heat_map
                )
        )

    def log_best_solution(self):
        print("-----------------------------")
        print(f"Best solution: {self.best_solution}")
        print(f"Best score ->", end=" ")
        print(f"Total: {round(self.best_score.total_score, 2)} ", end=" ")
        print(f"Purchases: {round(self.best_score.adjusted_purchases, 2)}", end=" ")
        print(f"Steps: {round(self.best_score.adjusted_steps, 2)}")
        print("-----------------------------")
        print()
        self.iterations.append(
            Iteration(
                self.best_solution, 
                self.best_score, 
                -1, 
                self.best_walk_heat_map,
                self.best_impulse_heat_map
                )
        )

    def _get_best_neighbor(self, tries_allowed: int = 5, swap_walkable_cells: bool = False) -> Neighbor:
        while tries_allowed > 0:
            tries_allowed -= 1
            neighbors = gen_neighbors(
                self.current_solution, 
                n=30, 
                swap_amount=3, 
                swap_walkable_cells=swap_walkable_cells
                )
            
            # Filtrar vecinos no tabú
            valid_neighbors = [
                n for n in neighbors
                if self._solution_hash(n) not in self.tabu_list
            ]

            best_grid = valid_neighbors[0]
            res = self.evaluate_solution(valid_neighbors[0])
            best_score = res.score
            best_walk_heat_map = res.walk_heat_map
            best_impulse_heat_map = res.impulse_heat_map
            for neighbor in valid_neighbors[1:]:
                eval_res = self.evaluate_solution(neighbor)
                if eval_res.score.total_score > best_score.total_score:
                    best_grid = neighbor
                    best_score = eval_res.score
                    best_walk_heat_map = eval_res.walk_heat_map
                    best_impulse_heat_map = eval_res.impulse_heat_map

            worst_allowed = self.current_score.total_score - abs(self.current_score.total_score*0.05)

            if best_score.total_score > worst_allowed:
                return Neighbor(
                    grid=best_grid,
                    score=best_score,
                    walk_heat_map=best_walk_heat_map,
                    impulse_heat_map=best_impulse_heat_map,
                    is_worth_exploring=True
                )

        return Neighbor(
            grid=self.current_solution,
            score=self.current_score,
            walk_heat_map=self.current_walk_heat_map,
            impulse_heat_map=self.current_impulse_heat_map,
            is_worth_exploring=False
        )


    def optimize(
            self, 
            iterations: int = 10, 
            tabu_size: int = 10, 
            tries_allowed: int = 5,
            swap_walkable_cells: bool = True,
            ) -> Tuple[SupermarketGrid, TabuSearchScore]:
        for cur_iter in range(iterations):

            best_neighbor = self._get_best_neighbor(
                tries_allowed=tries_allowed,
                swap_walkable_cells=swap_walkable_cells
                )

            if not best_neighbor.is_worth_exploring:
                print("No se encontró un mejor vecino.")
                break
            
            # Actualizar lista tabú
            self.tabu_list.append(self._solution_hash(best_neighbor.grid))
            if len(self.tabu_list) > tabu_size:
                self.tabu_list.pop(0)
            
            self.current_solution = best_neighbor.grid
            self.current_score = best_neighbor.score
            self.current_walk_heat_map = best_neighbor.walk_heat_map
            self.current_impulse_heat_map = best_neighbor.impulse_heat_map

            if best_neighbor.score.total_score > self.best_score.total_score:
                self.best_solution = self.current_solution
                self.best_score = self.current_score
                self.best_walk_heat_map = self.current_walk_heat_map
                self.best_impulse_heat_map = self.current_impulse_heat_map
            self.log_iteration((cur_iter+1))
        
        self.log_best_solution()
        return self.best_solution, self.best_score

    # Definir una función para generar una clave única para la solución
    def _solution_hash(self, solution: SupermarketGrid):
        """Genera una clave única para la solución"""

        matrix_tuple = tuple(tuple(id for cell_info in row) for row in solution.grid)

        rows: List[List[int]] = []
        for row in solution.grid:
            row_ids: List[int] = []
            for cell_info in row:
                row_ids.append(cell_info.aisle_id)
            rows.append(row_ids)

        matrix_tuple = tuple(tuple(row) for row in rows)

        matrix_str = str(matrix_tuple)  # Convert matrix to a string
        return hashlib.sha256(matrix_str.encode('utf-8')).hexdigest()