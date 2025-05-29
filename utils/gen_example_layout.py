import os
import json
import numpy as np
from core.grid import SupermarketGrid, GridInput
import config as cfg


def gen_example_layout() -> SupermarketGrid:
    """
    Generate a supermarket layout with aisles alternating between highest and lowest impulse indexes.
    Layout fills from top to bottom, left to right.
    """
    # Load aisle data
    with open(cfg.AISLE_INFO_FILE, "r") as file:
        aisles_data = json.load(file)

    # print("Aisles data loaded:", len(aisles_data.keys()))

    # Sort aisle IDs by impulse_index
    aisle_ids_with_impulse = []
    for aisle_id, data in aisles_data.items():
        aisle_ids_with_impulse.append((int(aisle_id), data.get("impulse_index", 0)))

    # Sort by impulse_index (descending)
    aisle_ids_with_impulse.sort(key=lambda x: x[1], reverse=True)

    # Extract just the IDs
    sorted_aisle_ids = [id for id, _ in aisle_ids_with_impulse]

    # Rearrange to alternate between highest and lowest impulse
    alternating_aisle_ids = []
    high_idx = 0
    low_idx = len(sorted_aisle_ids) - 1

    while high_idx <= low_idx:
        # Add highest impulse aisle
        if high_idx <= low_idx:
            alternating_aisle_ids.append(sorted_aisle_ids[high_idx])
            high_idx += 1

        # Add lowest impulse aisle
        if high_idx <= low_idx:
            alternating_aisle_ids.append(sorted_aisle_ids[low_idx])
            low_idx -= 1

    # Determine dimensions for a realistic supermarket layout
    rows = 36
    cols = 35

    # print(len(alternating_aisle_ids), "aisles to place in the grid.")

    # Create empty grid (all zeros = walkable aisles)
    grid = np.zeros((rows, cols), dtype=int)

    # Create entrance and exit at different locations
    grid[0][5] = -2  # Entrance (-2)
    grid[0][25] = -1  # Exit (-1)

    # Counter to track current aisle being placed
    current_aisle_idx = 0
    placed_aisles = 0

    # Place shelves in a pattern - filling from top to bottom, then left to right
    for c in range(1, cols - 1, 5):  # Iterate through columns
        for r in range(3, rows - 1, 3):  # Then through rows
            # Skip if we've placed all aisles
            if current_aisle_idx >= len(alternating_aisle_ids):
                break

            # Get current aisle ID (alternating highest/lowest impulse)
            aisle_id = alternating_aisle_ids[current_aisle_idx]

            # Place 3 shelf cells for this aisle side by side
            grid[r][c] = aisle_id
            grid[r][c + 1] = aisle_id
            grid[r][c + 2] = aisle_id

            placed_aisles += 1

            # Move to next aisle
            current_aisle_idx += 1

            # Place shelves on opposite side of aisle if there's another aisle
            if current_aisle_idx < len(alternating_aisle_ids):
                aisle_id = alternating_aisle_ids[current_aisle_idx]
                grid[r + 1][c] = aisle_id
                grid[r + 1][c + 1] = aisle_id
                grid[r + 1][c + 2] = aisle_id
                current_aisle_idx += 1
                placed_aisles += 1

    # print(f"Placed {placed_aisles} aisles in the grid.")

    # Create grid input and supermarket grid
    grid_input = GridInput(rows=rows, cols=cols, grid=grid.tolist(), entrance=(0, 5), exit=(0, 25))

    super_grid = SupermarketGrid.from_dict(grid_input, aisle_info_file=cfg.AISLE_INFO_FILE)

    return super_grid
