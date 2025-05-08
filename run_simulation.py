from core.grid import SupermarketGrid
# from optimization.tabu_search import TabuSearchOptimizer
from utils.helpers import load_shopping_lists
import config as cfg
from core.customer import CustomerSimulator
from typing import List, Dict, Any, Tuple

def main():
    # Cargar datos
    initial_grid = SupermarketGrid.from_file(cfg.LAYOUT_FILE, cfg.AISLE_INFO_FILE)
    shopping_lists = load_shopping_lists(cfg.CUSTOMERS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)
        
    for customer in customers:
        result = customer.simulate(initial_grid)
        print(result)

    # # Optimizar
    # optimizer = TabuSearchOptimizer(initial_grid, customers)
    # result = optimizer.evaluate_solution(initial_grid)
    # print(f"Initial evaluation: {result}")
    # best_layout, best_shopping_score, best_effort_score = optimizer.optimize(
    #     iterations=cfg.TABU_ITERATIONS,
    #     tabu_size=cfg.TABU_SIZE
    # )

    # print(best_layout.grid)
    # print(best_shopping_score)
    # print(best_effort_score)
    
    # # Guardar resultados
    # save_layout(SupermarketGrid.from_dict(best_layout), "optimized_layout.json")
    # print(f"Optimización completada. Mejor score: {best_score}")
    

if __name__ == "__main__":
    main()