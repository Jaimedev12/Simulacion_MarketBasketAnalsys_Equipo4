from core.grid import SupermarketGrid
# from optimization.tabu_search import TabuSearchOptimizer
from utils.helpers import load_shopping_lists
import config as cfg
from core.customer import CustomerSimulator
from optimization.layout_generator import get_grid_object
from typing import List, Dict, Any, Tuple
from utils.animate_path import animate_path

def main():
    # Cargar datos
    # initial_grid = SupermarketGrid.from_file(cfg.LAYOUT_FILE, cfg.AISLE_INFO_FILE)
    initial_grid = get_grid_object(cfg.AISLE_INFO_FILE)
    shopping_lists = load_shopping_lists(cfg.SHOPPING_LISTS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)
        
    result = customers[0].simulate(initial_grid)
    print(result)

    animate_path(initial_grid, result.path, 100)

if __name__ == "__main__":
    main()