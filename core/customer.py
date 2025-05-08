from collections import deque
from dataclasses import dataclass
from operator import is_
import random
from copy import deepcopy
from typing import List, Any, Tuple, Set, Optional, Dict
from core.grid import SupermarketGrid
import networkx as nx

@dataclass
class SimulationResult:
    impulsive_purchases: int
    path: List[Tuple[int, int]] # Coords

class CustomerSimulator:
    def __init__(self, shopping_list: List[int]) -> None:
        self.shopping_list:List[int] = shopping_list

    def get_product_ids_by_aisle(self, grid: SupermarketGrid) -> Dict[int, List[int]]:
        """
        Get the product IDs from the shopping list by aisle.
        Each aisle can have multiple products, so we need to randomly select one product ID from each aisle to look for.

        Returns:
            Dict[int, List[int]]: A dictionary where the keys are aisle IDs and the values are lists of product IDs.
        """
        
        aisle_with_product_ids : Dict[int, List[int]] = dict()
        for aisle_id in self.shopping_list:
            if aisle_id in grid.aisle_info.keys():
                # Get the product IDs from the aisle info
                product_count = grid.aisle_info[aisle_id].product_count
                if aisle_id not in aisle_with_product_ids.keys():
                    aisle_with_product_ids[aisle_id] = []
                aisle_with_product_ids[aisle_id].append(random.randint(1, product_count))

        return aisle_with_product_ids

    def get_surrounding_shelves(self, pos: Tuple[int, int], grid: SupermarketGrid) -> List[Tuple[int, int]]:
        shelves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= nx < grid.rows and 0 <= ny < grid.cols:
                cell_info = grid.grid[nx][ny]
                if cell_info.aisle_id > 0:
                    shelves.append((nx, ny))

        return shelves

    def find_closest_aisle(self, 
                           current_pos: Tuple[int, int], 
                           aisles: Set[int], 
                           grid: SupermarketGrid, 
                           visited_shelves: Set[Tuple[int, int]]
                           ) -> Optional[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """
        Find the closest aisle to the current position using BFS.
        """
        if current_pos not in grid.graph:
            return None
        
        current_path: List[Tuple[int, int]] = []
        
        # BFS setup
        queue = deque([current_pos])
        visited = set()

        while queue:
            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)
            current_path.append(current)

            neighbor_shelves = self.get_surrounding_shelves(current, grid)

            for shelf in neighbor_shelves:
                if shelf in visited_shelves:
                    continue
                    
                shelf_info = grid.grid[shelf[0]][shelf[1]]
                if shelf_info.aisle_id in aisles:
                    return (shelf, current_path)

            for neighbor in grid.graph.neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)

        return None

    def simulate(self, grid: SupermarketGrid) -> SimulationResult:
        impulsive_purchases = 0
        path_taken: List[Tuple[int, int]] = []  # Track the complete path for analysis

        current_pos: Tuple[int, int] = grid.entrance
        aisles_with_product_ids = self.get_product_ids_by_aisle(grid)

        # Mientras haya productos en la lista de compras
        visited_aisles: Set[Tuple[int, int]] = set()
        while len(aisles_with_product_ids) > 0:
            remaining_ailes: Set[int] = set(aisles_with_product_ids.keys())
            # for aisle_id in aisles_with_product_ids.keys():
            #     if aisle_id not in visited_aisles:
            #         remaining_ailes.add(aisle_id)

            result = self.find_closest_aisle(current_pos, remaining_ailes, grid, visited_aisles)
            closest, path_to_shelf = result if result is not None else (None, [])
            if closest is None:
                raise Exception("No se puede llegar a ningún pasillo de la lista de compras.")
            
            current_pos = path_to_shelf[-1]  # Actualizar la posición actual al último paso del camino
            closest_info = grid.grid[closest[0]][closest[1]]
            is_a_product_found = False
            for product_id in aisles_with_product_ids[closest_info.aisle_id]:
                if product_id >= closest_info.product_id_range[0] and product_id < closest_info.product_id_range[1]:
                    # Se encontró el producto, se elimina de la lista de compras
                    aisles_with_product_ids[closest_info.aisle_id].remove(product_id)
                    if len(aisles_with_product_ids[closest_info.aisle_id]) == 0:
                        del aisles_with_product_ids[closest_info.aisle_id]
                    is_a_product_found = True
                    break

            if is_a_product_found:
                # Se encontró un producto, se limpia la lista de pasillos visitados
                visited_aisles.clear()
                path_taken.extend(path_to_shelf[1:])  # Add the path to the shelf

            else:
                # No se encontró un producto, se agrega el pasillo a la lista de visitados
                visited_aisles.add(closest)
    
        path_to_exit = grid.get_path(path_taken[-1], grid.exit)
        if path_to_exit is None:
            raise Exception("No se puede llegar a la salida desde el último pasillo visitado.")
        path_taken.extend(path_to_exit[1:])


        return SimulationResult(
            impulsive_purchases=impulsive_purchases,
            path=path_taken
        )