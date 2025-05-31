# from optimization.tabu_search import TabuSearchOptimizer
import random
from dataclasses import dataclass
from typing import List
import concurrent.futures

import config as cfg
import utils.gen_multiple_layouts as gen_multiple_layouts
from core.customer import CustomerSimulator
from core.grid import SupermarketGrid
from optimization.result_interpreter import ResultInterpreter
from optimization.tabu_search import TabuSearchOptimizer
from utils.helpers import load_shopping_lists


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


def gen_simulations() -> List[SimulationConfig]:
    # ideal_layout = gen_example_layout()
    # ordered_grid = get_grid_object(1.0)
    # random_grid = get_grid_object(0.0)
    # balanced_grid = get_grid_object(0.5)

    # sims: List[SimulationConfig] = [
    #     # ---------------- Efrain ----------------
    #     SimulationConfig(layout=ordered_grid, name="ordered_layout"),
    #     SimulationConfig(layout=random_grid, name="random_layout"),
    #     SimulationConfig(layout=balanced_grid, name="balanced_layout"),
    #     # ---------------- Christopher ----------------
    #     SimulationConfig(
    #         layout=ideal_layout, name="ideal_layout", swap_walkable=False, swap_whole_aisles=True, swap_amount=1
    #     ),
    # ]

    # # ---------------- Jaime ----------------
    # for i in range(1, 11, 2):
    #     balanced_grid_copy = deepcopy(balanced_grid)
    #     sims.append(SimulationConfig(layout=balanced_grid_copy,
    #     name=f"swap_amount_{i}", swap_amount=i))
    layouts = gen_multiple_layouts.get_all_layouts()
    sims: List[SimulationConfig] = []
    for layout in layouts:
        sims.append(
            SimulationConfig(
                layout=layout["layout"],
                name=layout["name"],
                swap_walkable=False,
                swap_whole_aisles=True,
                swap_amount=1,
            )
        )

    return sims


def run_simulation(sim_config, selected_customers):
    search_optimizer = TabuSearchOptimizer(sim_config.layout, customers=selected_customers)
    interpreter = ResultInterpreter()
    print(f"Running simulation for {sim_config.name}")
    search_optimizer.change_curr_grid(sim_config.layout, True, True)
    search_optimizer.optimize(
        iterations=sim_config.tabu_iterations,
        tabu_size=sim_config.tabu_size,
        tries_allowed=sim_config.tries_allowed,
        swap_amount=sim_config.swap_amount,
        swap_walkable_cells=sim_config.swap_walkable,
        swap_whole_aisles=sim_config.swap_whole_aisles,
    )
    interpreter.update_iterations(search_optimizer.iterations)
    interpreter.store(filename=f"{sim_config.name}.npz")


def main():
    sim_configs = gen_simulations()

    shopping_lists = load_shopping_lists(cfg.SHOPPING_LISTS_FILE)

    customers: List[CustomerSimulator] = []
    for shopping_list in shopping_lists:
        customer = CustomerSimulator(shopping_list)
        customers.append(customer)

    selected_customers = random.sample(customers, cfg.CUSTOMER_COUNT)

    print(len(sim_configs), "simulations to run")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(run_simulation, sim_config, selected_customers) for sim_config in sim_configs]
        concurrent.futures.wait(futures)
    # for sim_config in sim_configs:
    #     run_simulation(sim_config, selected_customers)


if __name__ == "__main__":
    main()
