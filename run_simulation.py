from core.grid import SupermarketGrid
# from optimization.tabu_search import TabuSearchOptimizer
from utils.helpers import load_shopping_lists
import config as cfg
from core.customer import CustomerSimulator, SimulationResult
from optimization.layout_generator import get_grid_object
from typing import List, Dict, Any, Tuple
from utils.animate_path import animate_path
import random

def main():
    # Cargar datos
    # initial_grid = SupermarketGrid.from_file(cfg.LAYOUT_FILE, cfg.AISLE_INFO_FILE)
    initial_grid = get_grid_object(cfg.AISLE_INFO_FILE)
    shopping_lists = load_shopping_lists(cfg.SHOPPING_LISTS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)
        

    selected_customers = random.sample(customers, 2)

    for i, customer_to_simulate in enumerate(selected_customers):
        result: SimulationResult = customer_to_simulate.simulate(initial_grid)
        if result.path: # Check if path is not empty
            animate_path(initial_grid, result.path, speed=300) # Adjusted speed


if __name__ == "__main__":
    main()