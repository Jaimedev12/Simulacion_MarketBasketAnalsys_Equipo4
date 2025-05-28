from collections import deque
from dataclasses import dataclass
from os import path
import random
from copy import deepcopy
from typing import List, Any, Tuple, Set, Optional, Dict
from networkx import neighbors
from core.grid import SupermarketGrid
import networkx as nx

@dataclass
class SimulationResult:
    impulsive_purchases: int
    path: List[Tuple[int, int]] # Coords
    impulsive_shelfs: List[Tuple[int, int]] # Coords

@dataclass
class GetPathResult:
    """Result of finding the closest pending shelf path.
    
    Attributes:
        closest_shelf_pos: Position of the closest shelf.
        path_to_shelf: Path from start to the shelf.
        impulsive_purchases: Count of impulsive buys along the path.
        impulsive_shelfs: List of shelves where impulsive buys were made.
    """
    closest_shelf_pos: Tuple[int, int]
    path_to_shelf: List[Tuple[int, int]]
    impulsive_purchases: int

@dataclass
class TargetShelf:
    shelf_pos: Tuple[int, int]
    adj_walkable_pos: Tuple[int, int]


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

    def get_surrounding_shelves(self, pos: Tuple[int, int], grid: SupermarketGrid, include_exit: bool = False) -> List[Tuple[int, int]]:
        shelves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dx, dy in directions:
            nx_, ny = pos[0] + dx, pos[1] + dy
            if 0 <= nx_ < grid.rows and 0 <= ny < grid.cols:
                cell_info = grid.grid[nx_][ny]
                if cell_info.aisle_id > 0 or (include_exit and cell_info.is_exit):  # Aisle or exit
                    shelves.append((nx_, ny))

        return shelves

    def find_closest_from_set(self, 
                           start_pos: Tuple[int, int], 
                           pending_cell_ids: Set[int], 
                           grid: SupermarketGrid, 
                           visited_shelves: Set[Tuple[int, int]],
                           find_exit: bool = False
                           ) -> TargetShelf:
        if start_pos not in grid.graph:
            raise Exception("La posición inicial no es válida.")
        
        # BFS setup
        queue = deque([start_pos])
        visited = set()

        while queue:
            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)
            neighbor_shelves = self.get_surrounding_shelves(current, grid, include_exit=find_exit)

            for shelf in neighbor_shelves:
                shelf_id = grid.grid[shelf[0]][shelf[1]].aisle_id
                
                if shelf in visited_shelves:
                    continue
                    
                shelf_info = grid.grid[shelf[0]][shelf[1]]
                if shelf_info.is_exit and find_exit:
                    return TargetShelf(shelf, shelf)
                if shelf_info.aisle_id in pending_cell_ids:
                    return TargetShelf(shelf, current)

            for neighbor in grid.graph.neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)

        raise Exception("No se encontró un pasillo contiguo a la posición inicial.")

    def get_path_to_closest_pending(
            self, 
            start_pos: Tuple[int, int], 
            pending_cell_ids: Set[int],
            grid: SupermarketGrid,
            visited_shelves: Set[Tuple[int, int]],
            shelfs_with_impulsive_buys: Set[Tuple[int, int]],
            go_to_exit: bool = False
            ) -> GetPathResult:
        """
        Returns:
            GetPathResult object containing:
                - closest_shelf_pos: Position of the closest shelf
                - path_to_shelf: Path from start to the shelf
                - impulsive_purchases: Number of impulsive buys along the path
                - impulsive_shelfs: List of shelves where impulsive buys were made
        """
        
        result = self.find_closest_from_set(
            start_pos, 
            pending_cell_ids, 
            grid, 
            visited_shelves,
            find_exit=go_to_exit
            )
        
        closest_shelf, target_pos = result.shelf_pos, result.adj_walkable_pos
        
        impulsive_purchases = 0
        current_path = grid.get_path(start_pos, target_pos)
        if current_path is None:
            raise Exception("No se puede llegar a la estantería más cercana.")
        
        for cell in current_path:
            neighbor_shelves = self.get_surrounding_shelves(cell, grid)
            for shelf in neighbor_shelves:
                shelf_id = grid.grid[shelf[0]][shelf[1]].aisle_id
                shelf_impulse_index = grid.aisle_info[shelf_id].impulse_index
                if shelf not in shelfs_with_impulsive_buys:
                    if random.random() < shelf_impulse_index:
                        impulsive_purchases += 1
                        shelfs_with_impulsive_buys.add(shelf)
        
        return GetPathResult(
            closest_shelf, 
            current_path, 
            impulsive_purchases,
            )

    def simulate(self, grid: SupermarketGrid) -> SimulationResult:
        impulsive_purchases = 0
        path_taken: List[Tuple[int, int]] = []  # Track the complete path for analysis

        current_pos: Tuple[int, int] = grid.entrance
        aisles_with_product_ids = self.get_product_ids_by_aisle(grid)

        # Mientras haya productos en la lista de compras
        visited_aisles: Set[Tuple[int, int]] = set()
        shelves_already_bought: Set[Tuple[int, int]] = set()
        while True:
            remaining_ailes: Set[int] = set(aisles_with_product_ids.keys())

            result = self.get_path_to_closest_pending(
                current_pos, 
                remaining_ailes, 
                grid, 
                visited_aisles, 
                shelves_already_bought,
                go_to_exit=(len(remaining_ailes) == 0)
                )
            
            closest = result.closest_shelf_pos
            path_to_shelf = result.path_to_shelf
            impulsive_purchases_in_path = result.impulsive_purchases

            path_taken.extend(path_to_shelf[1:])  # Add the path to the shelf
            impulsive_purchases += impulsive_purchases_in_path

            if len(remaining_ailes) == 0:
                break

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
            else:
                # No se encontró un producto, se agrega el pasillo a la lista de visitados
                visited_aisles.add(closest)
    
        return SimulationResult(
            impulsive_purchases=impulsive_purchases,
            path=path_taken,
            impulsive_shelfs=list(shelves_already_bought)
        )