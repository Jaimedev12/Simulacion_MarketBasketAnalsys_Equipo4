import random
from copy import deepcopy

class CustomerSimulator:
    def __init__(self, grid):
        self.grid = grid

    def simulate(self, shopping_list):
        current_pos = self.grid.entrance
        remaining_items = set(deepcopy(shopping_list))
        impulsive_purchases = 0
        path_taken = []  # Track the complete path for analysis

        # Process the planned shopping list
        while remaining_items:
            # Check if any items in the shopping list have locations in the grid
            available_aisles = []
            for aisle_id in remaining_items:
                if aisle_id in self.grid.aisle_info and "cells" in self.grid.aisle_info[aisle_id]:
                    available_aisles.append(aisle_id)
            
            if not available_aisles:
                break  # No more accessible items
            
            # Find the closest aisle from the current position
            target_aisle = min(
                available_aisles, 
                key=lambda aisle_id: min(
                    [abs(current_pos[0]-cell[0]) + abs(current_pos[1]-cell[1]) 
                    for cell in self.grid.aisle_info[aisle_id]["cells"]]
                )
            )
            
            # Get a specific target cell in the target aisle
            target_cells = self.grid.aisle_info[target_aisle]["cells"]
            target_pos = min(
                target_cells,
                key=lambda pos: abs(current_pos[0]-pos[0]) + abs(current_pos[1]-pos[1])
            )
            
            # Calculate path to the target
            path = self.grid.get_path(current_pos, target_pos)
            if not path:
                break  # No valid path found
            
            path_taken.extend(path)
            
            # Move along the path and check for impulse purchases
            for step_pos in path[1:]:  # Skip starting position
                x, y = step_pos
                cell_value = self.grid.grid[x][y]
                
                # Check if the customer passes by an aisle (positive cell value)
                if cell_value > 0 and cell_value not in shopping_list:
                    # Retrieve aisle's impulse index
                    if cell_value in self.grid.aisle_info:
                        impulse_index = self.grid.aisle_info[cell_value].get('impulse_index', 0.0)
                        # Check for impulse purchase
                        if random.random() < impulse_index:
                            impulsive_purchases += 1
            
            # Update position and remove the item from shopping list
            current_pos = target_pos
            remaining_items.remove(target_aisle)
        
        # Calculate path to exit
        exit_path = self.grid.get_path(current_pos, self.grid.exit)
        if exit_path:
            path_taken.extend(exit_path[1:])  # Skip the current position
            
            # Check for impulse purchases on the way to exit
            for step_pos in exit_path[1:]:
                x, y = step_pos
                cell_value = self.grid.grid[x][y]
                
                if cell_value > 0 and cell_value not in shopping_list:
                    if cell_value in self.grid.aisle_info:
                        impulse_index = self.grid.aisle_info[cell_value].get('impulse_index', 0.0)
                        if random.random() < impulse_index:
                            impulsive_purchases += 1
        
        return {
            'impulsive_purchases': impulsive_purchases,
            'path': path_taken
        }