# from optimization.tabu_search import TabuSearchOptimizer
from dataclasses import dataclass
from os import name
from re import S
from utils.helpers import load_shopping_lists
import config as cfg
from core.customer import CustomerSimulator
from optimization.layout_generator import get_grid_object
from typing import List
import random
from optimization.tabu_search import TabuSearchOptimizer
from optimization.result_interpreter import ResultInterpreter
from utils.gen_example_layout import gen_example_layout
from utils.visualization import plot_grid
from core.grid import SupermarketGrid

@dataclass
class SimulationConfig:
    layout: SupermarketGrid
    name: str
    tabu_iterations: int = cfg.TABU_ITERATIONS
    tabu_size: int = cfg.TABU_SIZE
    tries_allowed: int = cfg.TABU_TRIES_ALLOWED
    swap_walkable: bool = True
    swap_amount: int = 5
    swap_whole_aisles: bool = False

def gen_simulations()-> List[SimulationConfig]:
    ideal_layout = gen_example_layout()
    ordered_grid = get_grid_object(1.0)
    random_grid = get_grid_object(0.0)
    balanced_grid = get_grid_object(0.5)
    
    sims: List[SimulationConfig] = [
        # SimulationConfig(layout=ordered_grid, name="ordered_layout"),
        # SimulationConfig(layout=random_grid, name="random_layout"),
        # SimulationConfig(layout=balanced_grid, name="balanced_layout"),
        SimulationConfig(layout=ideal_layout, name="ideal_layout", swap_walkable=False, swap_whole_aisles=True, swap_amount=1),
    ]

    # for i in range(1, 5):
    #     balanced_grid_alt = get_grid_object(0.5)
    #     sims.append(SimulationConfig(layout=balanced_grid_alt, name=f"swap_amount_{i*3}", swap_amount=i*3))

    return sims


def main():
    # Cargar datos
    # ordered_grid = SupermarketGrid.from_file(cfg.LAYOUT_FILE, cfg.AISLE_INFO_FILE)
    sim_configs = gen_simulations()

    # plot_grid(sim_configs[0].layout)
    
    shopping_lists = load_shopping_lists(cfg.SHOPPING_LISTS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)
        
    selected_customers = random.sample(customers, cfg.CUSTOMER_COUNT)

    interpreter = ResultInterpreter()
    search_optimizer = TabuSearchOptimizer(sim_configs[0].layout, customers=selected_customers)

    for sim_config in sim_configs:
        print(f"Running simulation for {sim_config.name}")
        search_optimizer.change_curr_grid(sim_config.layout, True, True)
        search_optimizer.optimize(iterations=sim_config.tabu_iterations, tabu_size=sim_config.tabu_size,
                                  tries_allowed=sim_config.tries_allowed, swap_amount=sim_config.swap_amount, 
                                  swap_walkable_cells=sim_config.swap_walkable, swap_whole_aisles=sim_config.swap_whole_aisles)

        interpreter.update_iterations(search_optimizer.iterations)
        interpreter.store(filename=f"{sim_config.name}.npz")

if __name__ == "__main__":
    main()