import json
import numpy as np
import sys
import os
# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg

def main():
    # Load aisle data
    with open("../" + cfg.AISLE_INFO_FILE, 'r') as file:
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
    
    # Save the grid to a file
    output_path = "../data/example_layout.json"
    with open(output_path, 'w') as file:
        json.dump({
            "rows": rows,
            "cols": cols,
            "grid": grid.tolist(),
            "entrance": [0, 5],
            "exit": [0, 25]
        }, file, indent=4)
    
    print(f"Example supermarket layout created and saved to {output_path}")
    
    # Save the grid visualization to a file
    viz_path = "../data/layout_visualization.txt"
    with open(viz_path, 'w') as viz_file:
        viz_file.write("Layout visualization (numbers = aisle IDs, 0 = walkable space):\n\n")
        for row in grid:
            viz_file.write(" ".join(f"{cell:3d}" for cell in row) + "\n")
    
    print(f"Visualization saved to {viz_path}")

if __name__ == "__main__":
    main()