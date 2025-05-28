import json
import numpy as np
from core.grid import SupermarketGrid, GridInput
import config as cfg

def gen_example_layout() -> SupermarketGrid:
    # Load aisle data
    with open(cfg.AISLE_INFO_FILE, 'r') as file:
        aisles_data = json.load(file)
    
    # Determine dimensions for a realistic supermarket layout
    # For 134 aisles with 3 cells each = 402 shelf cells + walking space
    rows = 37
    cols = 30
    
    # Create empty grid (all zeros = walkable aisles)
    grid = np.zeros((rows, cols), dtype=int)
    
    # Create entrance and exit at different locations
    grid[0][5] = -1  # Entrance (-1)
    grid[0][25] = -2  # Exit (-2)
    
    # Place shelves in a realistic supermarket layout pattern
    aisle_ids = [int(id) for id in aisles_data.keys()]
    
    # Counter to track current aisle being placed
    current_aisle_idx = 0
    
    # Place shelves in a pattern with walking aisles between them
    for r in range(3, rows, 3):
        for c in range(1, cols-1, 5):
            # Skip if we've placed all aisles
            if current_aisle_idx >= len(aisle_ids):
                break
                
            # Get current aisle ID
            aisle_id = aisle_ids[current_aisle_idx]
            
            # Place 3 shelf cells for this aisle side by side
            grid[r][c] = aisle_id
            grid[r][c+1] = aisle_id
            grid[r][c+2] = aisle_id
            
            # Move to next aisle
            current_aisle_idx += 1
            
            # Place shelves on opposite side of aisle if there's another aisle
            if current_aisle_idx < len(aisle_ids):
                aisle_id = aisle_ids[current_aisle_idx]
                grid[r+1][c] = aisle_id
                grid[r+1][c+1] = aisle_id
                grid[r+1][c+2] = aisle_id
                current_aisle_idx += 1

    grid_input = GridInput(
        rows=rows,
        cols=cols,
        grid=grid.tolist(),
        entrance=(0, 5),
        exit=(0, 25)
    )

    super_grid = SupermarketGrid.from_dict(grid_input, aisle_info_file=cfg.AISLE_INFO_FILE)
    
    return super_grid
