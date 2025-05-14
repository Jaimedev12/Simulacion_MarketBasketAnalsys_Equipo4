from copy import deepcopy

from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from core.grid import SupermarketGrid, CellInfo
from core.customer import CustomerSimulator
from .neighborhood import gen_neighbors
from typing import List, Tuple
import hashlib
import os
from optimization.layout_generator import generate_individual_plot

class TabuSearchOptimizer:
    def __init__(self, initial_grid: SupermarketGrid, customers: List[CustomerSimulator]):
        self.current_solution: SupermarketGrid= initial_grid
        self.tabu_list = []
        self.customers: List[CustomerSimulator] = customers
        self.best_solution: SupermarketGrid = deepcopy(self.current_solution)
        self.best_score: float = self.evaluate_solution(self.current_solution)
        

    def evaluate_solution(self, solution: SupermarketGrid) -> float:
        """Evalúa una solución con simulaciones de clientes"""
        total_score: float = 0.0
        for customer in self.customers:
            result = customer.simulate(solution)
            num_products = len(customer.shopping_list)

            adjusted_purchases = result.impulsive_purchases / num_products
            adjusted_steps = len(result.path) / num_products
            total_score += adjusted_purchases - adjusted_steps
        return total_score

    def log_iteration(self, iteration: int, save_img: bool = False):
        print(f"Iteration {iteration}: Best score: {self.best_score}")
        cur_solution_plot = generate_individual_plot(self.current_solution)

        if isinstance(cur_solution_plot.axes.figure, Figure) and save_img: 
            os.makedirs("iterations", exist_ok=True)
            cur_solution_plot.axes.figure.savefig(f"iterations/iteration_{iteration+1}.png")


    def optimize(self, iterations: int = 10, tabu_size: int = 10) -> Tuple[SupermarketGrid, float]:
        for cur_iter in range(iterations):
            # Generar vecinos
            neighbors = gen_neighbors(self.current_solution, n=10, swap_amount=10)
            
            # Filtrar vecinos no tabú
            valid_neighbors = [
                n for n in neighbors
                if self._solution_hash(n) not in self.tabu_list
            ]
            
            # Evaluar y seleccionar mejor vecino
            best_neighbor = valid_neighbors[0]
            best_score = self.evaluate_solution(valid_neighbors[0])
            for neighbor in valid_neighbors[1:]:
                score = self.evaluate_solution(neighbor)
                if score > best_score:
                    best_neighbor = neighbor
                    best_score = score
            
            # Actualizar mejor solución global
            if best_score > self.best_score:
                self.best_solution = best_neighbor
                self.best_score = best_score
            
            # Actualizar lista tabú
            self.tabu_list.append(self._solution_hash(best_neighbor))
            if len(self.tabu_list) > tabu_size:
                self.tabu_list.pop(0)
            
            self.current_solution = best_neighbor
            save_img: bool = cur_iter % 5 == 0
            self.log_iteration(cur_iter, save_img=save_img)
        
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