from copy import deepcopy
from core.grid import SupermarketGrid
from core.customer import CustomerSimulator
from .neighborhood import swap_cells, move_category, rotate_section

class TabuSearchOptimizer:
    def __init__(self, initial_grid, customers_data):
        self.current_solution = initial_grid
        self.best_solution = deepcopy(self.current_solution)
        self.best_sales_score = -1
        self.best_effort_score = 1e9
        self.tabu_list = []
        self.customers_data = customers_data

    def evaluate_solution(self, solution):
        """Evalúa una solución con simulaciones de clientes"""
        grid = SupermarketGrid.from_dict(solution)
        total = 0
        for customer_list in self.customers_data:
            simulator = CustomerSimulator(grid)
            total += simulator.simulate(customer_list)
        return total

    def optimize(self, iterations=10, tabu_size=10):
        for _ in range(iterations):
            # Generar vecinos
            neighbors = [
                swap_cells(deepcopy(self.current_solution)),
                move_category(deepcopy(self.current_solution)),
                rotate_section(deepcopy(self.current_solution))
            ]
            
            # Filtrar vecinos no tabú
            valid_neighbors = [
                n for n in neighbors
                if self._solution_hash(n) not in self.tabu_list
            ]
            
            # Evaluar y seleccionar mejor vecino
            best_neighbor = None
            best_score = -1
            for neighbor in valid_neighbors:
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
        
        return self.best_solution, self.best_score

    # Definir una función para generar una clave única para la solución
    def _solution_hash(self, solution):
        """Genera una clave única para la solución"""
        cells = sorted(solution["cells"], key=lambda x: (x["row"], x["col"]))
        return hash(str(cells))