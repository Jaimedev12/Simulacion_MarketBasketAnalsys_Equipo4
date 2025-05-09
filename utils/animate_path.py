import sys
import os

# Add the project root directory to the Python path
# os.path.abspath(__file__) gives the absolute path of the current script (animate_path.py)
# os.path.dirname(...) gets the directory of the script (utils)
# os.path.dirname(os.path.dirname(...)) gets the parent of that directory (Simulacion)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.grid import SupermarketGrid, CellInfo # Assuming CellInfo is needed for type hints if you inspect grid directly
# from optimization.tabu_search import TabuSearchOptimizer
import config as cfg
from typing import List, Tuple

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.colors import ListedColormap

def animate_path(grid: SupermarketGrid, path: List[Tuple[int, int]], speed: int = 500) -> None:

    # Create a numerical representation of the grid for display
    # 0: Walkable, 1: Aisle/Shelf
    grid_layout_matrix = np.zeros((grid.rows, grid.cols), dtype=int)
    for r in range(grid.rows):
        for c in range(grid.cols):
            # grid.grid[r][c] is a CellInfo object
            cell_info: CellInfo = grid.grid[r][c]
            if cell_info.aisle_id > 0:  # If it's an aisle/shelf
                grid_layout_matrix[r, c] = 1
            # Walkable areas (aisle_id == 0 or not an aisle) remain 0

    cmap = ListedColormap(['white', 'lightgray'])  # 0: white (walkable), 1: lightgray (aisle)

    fig, ax = plt.subplots(figsize=(max(2, grid.cols / 3), max(2, grid.rows / 5)))
    ax.set_title("Supermarket Path Animation")

    # Display the grid layout
    # origin='upper' means (0,0) is top-left, matching matrix indexing
    # interpolation='nearest' gives sharp cell boundaries
    ax.imshow(grid_layout_matrix, cmap=cmap, origin='upper', interpolation='nearest')

    # Mark entrance and exit
    # Path coordinates are (row, col). For plotting, plot(col, row).
    if grid.entrance:
        ax.plot(grid.entrance[1], grid.entrance[0], 'go', markersize=6, label='Entrance')
    if grid.exit:
        ax.plot(grid.exit[1], grid.exit[0], 'ro', markersize=6, label='Exit')

    # Plot the full path faintly (optional)
    if len(path) > 0:
        path_cols = [p[1] for p in path]  # Column indices
        path_rows = [p[0] for p in path]  # Row indices
        ax.plot(path_cols, path_rows, 'b-', alpha=0.3, linewidth=2, label='Full Path')

    # Customer marker
    customer_marker, = ax.plot([], [], 'o', color='dodgerblue', markersize=8, label='Customer')

    # Configure plot appearance
    ax.set_xticks(np.arange(grid.cols))
    ax.set_yticks(np.arange(grid.rows))
    ax.set_xticklabels(np.arange(grid.cols))
    ax.set_yticklabels(np.arange(grid.rows))
    # Minor ticks for grid lines between cells
    ax.set_xticks(np.arange(-.5, grid.cols, 1), minor=True)
    ax.set_yticks(np.arange(-.5, grid.rows, 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", size=0) # Hide minor tick marks themselves
    
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1)) # Adjust legend position
    fig.tight_layout(rect=(0, 0, 0.85, 1)) # Adjust layout to make space for legend

    def init_animation():
        customer_marker.set_data([], [])
        return customer_marker,

    def update_animation(frame_index):
        # path contains (row, col) tuples
        # For ax.plot(x, y), x is column, y is row
        current_row, current_col = path[frame_index]
        customer_marker.set_data([current_col], [current_row])
        return customer_marker,

    # Create animation
    # interval is the delay between frames in milliseconds
    # repeat=False stops the animation after one run
    ani = animation.FuncAnimation(fig, update_animation, frames=len(path),
                                  init_func=init_animation, blit=True, interval=speed, repeat=False)

    plt.show()


if __name__ == "__main__":
    grid = SupermarketGrid.from_file("../data/example_layout.json", "../data/aisle_info.json")
    animate_path(grid=grid, path=[(0, 0), (1, 0), (2, 0), (1, 0), (0, 0)])  # Example path for testing