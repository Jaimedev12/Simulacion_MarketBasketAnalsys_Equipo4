# from optimization.tabu_search import TabuSearchOptimizer
from utils.helpers import load_shopping_lists
import config as cfg
from core.customer import CustomerSimulator
from optimization.layout_generator import get_grid_object
from typing import List
import random
from optimization.tabu_search import TabuSearchOptimizer
from optimization.result_interpreter import ResultInterpreter

def main():
    # Cargar datos
    # ordered_grid = SupermarketGrid.from_file(cfg.LAYOUT_FILE, cfg.AISLE_INFO_FILE)
    ordered_grid = get_grid_object(1.0)
    random_grid = get_grid_object(0.0)
    balanced_grid = get_grid_object(0.5)
    
    shopping_lists = load_shopping_lists(cfg.SHOPPING_LISTS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)
        
    selected_customers = random.sample(customers, cfg.CUSTOMER_COUNT)

    search_optimizer = TabuSearchOptimizer(ordered_grid, customers=selected_customers)
    search_optimizer.optimize(iterations=cfg.TABU_ITERATIONS, tabu_size=cfg.TABU_SIZE)
    # search_optimizer.change_curr_grid(random_grid)
    # search_optimizer.optimize(iterations=cfg.TABU_ITERATIONS, tabu_size=cfg.TABU_SIZE)
    # search_optimizer.change_curr_grid(balanced_grid)
    # search_optimizer.optimize(iterations=cfg.TABU_ITERATIONS, tabu_size=cfg.TABU_SIZE)
    

    interpreter = ResultInterpreter(search_optimizer.iterations)
    interpreter.store()
    
    search_result = interpreter.read_results()
    for it in search_result:
        print(it.iteration_num)
        print(it.walk_heat_map)
        print(it.impulse_heat_map)
        print()

    # plot_multiple_grids([ordered_grid, search_result[0]], ["Initial Grid", "Optimized Grid"])

    # for i, customer_to_simulate in enumerate(selected_customers):
    #     result: SimulationResult = customer_to_simulate.simulate(ordered_grid)
    #     if result.path: # Check if path is not empty
    #         animate_path(ordered_grid, result.path, speed=300) # Adjusted speed


if __name__ == "__main__":
    main()