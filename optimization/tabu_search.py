from copy import deepcopy
from dataclasses import dataclass

from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from core.grid import SupermarketGrid, CellInfo
from core.customer import CustomerSimulator
from .neighborhood import gen_neighbors
from typing import List, Tuple
import hashlib
import os
from optimization.layout_generator import generate_individual_plot

@dataclass
class TabuSearchScore:
    total_score: float
    adjusted_purchases: float
    adjusted_steps: float

@dataclass
class Iteration:
    grid: SupermarketGrid
    score: TabuSearchScore
    iteration_num: int


class TabuSearchOptimizer:
    def __init__(self, initial_grid: SupermarketGrid, customers: List[CustomerSimulator]):
        self.current_solution: SupermarketGrid= initial_grid
        self.tabu_list = []
        self.customers: List[CustomerSimulator] = customers
        self.best_solution: SupermarketGrid = deepcopy(self.current_solution)
        self.best_score: TabuSearchScore = self.evaluate_solution(self.current_solution)
        self.current_score: TabuSearchScore = self.best_score
        self.iterations: List[Iteration] = [Iteration(initial_grid, self.best_score, 0)]
        
    def change_curr_grid(self, new_grid: SupermarketGrid, restart_score: bool = False):
        """Cambia la cuadrícula inicial"""
        self.current_solution = new_grid
        self.best_solution = deepcopy(self.current_solution)
        
        self.current_score = self.evaluate_solution(self.current_solution)
        self.tabu_list = []

        if restart_score:
            self.best_score = self.current_score

    def evaluate_solution(self, solution: SupermarketGrid) -> TabuSearchScore:
        """Evalúa una solución con simulaciones de clientes"""
        total_score: float = 0.0
        adjusted_purchases_sum: float = 0.0
        adjusted_steps_sum: float = 0.0
        for customer in self.customers:
            result = customer.simulate(solution)
            num_products = len(customer.shopping_list)

            adjusted_purchases = result.impulsive_purchases / num_products
            adjusted_steps = len(result.path) / num_products
            total_score += adjusted_purchases - adjusted_steps
            adjusted_purchases_sum += adjusted_purchases
            adjusted_steps_sum += adjusted_steps

        return TabuSearchScore(
            total_score/len(self.customers), 
            adjusted_purchases_sum/len(self.customers), 
            adjusted_steps=adjusted_steps_sum/len(self.customers)
            )

    def log_iteration(self, iteration: int):
        print(f"Iteration {iteration+1}: Best score: {self.best_score.total_score}")
        print(f"Current score ->", end=" ")
        print(f"Total: {round(self.current_score.total_score, 2)} ", end=" ")
        print(f"Purchases: {round(self.current_score.adjusted_purchases, 2)}", end=" ")
        print(f"Steps: {round(self.current_score.adjusted_steps, 2)}")
        self.iterations.append(
            Iteration(self.current_solution, self.current_score, iteration)
        )

    def log_best_solution(self):
        print()
        print(f"Best solution: {self.best_solution}")
        print(f"Best score ->", end=" ")
        print(f"Total: {round(self.best_score.total_score, 2)} ", end=" ")
        print(f"Purchases: {round(self.best_score.adjusted_purchases, 2)}", end=" ")
        print(f"Steps: {round(self.best_score.adjusted_steps, 2)}")
        self.iterations.append(
            Iteration(self.best_solution, self.best_score, -1)
        )

    def _get_best_neighbor(self, tries_allowed: int = 5) -> Tuple[SupermarketGrid, TabuSearchScore, bool]:
        while tries_allowed > 0:
            tries_allowed -= 1
            neighbors = gen_neighbors(self.current_solution, n=30, swap_amount=3)
            
            # Filtrar vecinos no tabú
            valid_neighbors = [
                n for n in neighbors
                if self._solution_hash(n) not in self.tabu_list
            ]

            best_neighbor = valid_neighbors[0]
            best_score = self.evaluate_solution(valid_neighbors[0])
            for neighbor in valid_neighbors[1:]:
                score = self.evaluate_solution(neighbor)
                if score.total_score > best_score.total_score:
                    best_neighbor = neighbor
                    best_score = score

            worst_allowed = self.current_score.total_score - abs(self.current_score.total_score)

            if best_score.total_score > worst_allowed:
                return best_neighbor, best_score, True

        return self.current_solution, TabuSearchScore(0.0, 0.0, 0.0), False


    def optimize(
            self, 
            iterations: int = 10, 
            tabu_size: int = 10, 
            tries_allowed: int = 5
            ) -> Tuple[SupermarketGrid, TabuSearchScore]:
        for cur_iter in range(iterations):

            best_neighbor, best_score, is_worth_continuing = self._get_best_neighbor(tries_allowed=tries_allowed)

            if not is_worth_continuing:
                print("No se encontró un mejor vecino.")
                break
            
            # Actualizar lista tabú
            self.tabu_list.append(self._solution_hash(best_neighbor))
            if len(self.tabu_list) > tabu_size:
                self.tabu_list.pop(0)
            
            self.current_solution = best_neighbor
            self.current_score = best_score
            if best_score.total_score > self.best_score.total_score:
                self.best_solution = best_neighbor
                self.best_score = best_score
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