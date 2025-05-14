from re import search

from matplotlib.pyplot import plot
from core.grid import SupermarketGrid
# from optimization.tabu_search import TabuSearchOptimizer
from utils.helpers import load_shopping_lists
import config as cfg
from core.customer import CustomerSimulator, SimulationResult
from optimization.layout_generator import get_grid_object, plot_multiple_grids
from typing import List, Dict, Any, Tuple
from utils.animate_path import animate_path
import random
from optimization.tabu_search import TabuSearchOptimizer
from optimization.result_interpreter import ResultInterpreter

def main():
    # Cargar datos
    # initial_grid = SupermarketGrid.from_file(cfg.LAYOUT_FILE, cfg.AISLE_INFO_FILE)
    initial_grid = get_grid_object()
    shopping_lists = load_shopping_lists(cfg.SHOPPING_LISTS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)
        

    selected_customers = random.sample(customers, 3)

    search_optimizer = TabuSearchOptimizer(initial_grid, customers=selected_customers)
    search_optimizer.optimize(iterations=20, tabu_size=10)

    interpreter = ResultInterpreter(search_optimizer.iterations)
    interpreter.store()

    # plot_multiple_grids([initial_grid, search_result[0]], ["Initial Grid", "Optimized Grid"])

    # for i, customer_to_simulate in enumerate(selected_customers):
    #     result: SimulationResult = customer_to_simulate.simulate(initial_grid)
    #     if result.path: # Check if path is not empty
    #         animate_path(initial_grid, result.path, speed=300) # Adjusted speed


if __name__ == "__main__":
    main()