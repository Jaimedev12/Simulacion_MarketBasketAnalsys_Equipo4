import matplotlib.pyplot as plt
import numpy as np
from core.grid import SupermarketGrid

def plot_grid(grid: SupermarketGrid):
    """Visualiza el layout del supermercado"""
    rows = grid.rows
    cols = grid.cols
    matrix = np.zeros((rows, cols))
    
    for x in range(rows):
        for y in range(cols):
            cell = grid.grid[x][y]
            if not cell.is_walkable:
                matrix[x][y] = grid.aisle_info[cell.aisle_id].impulse_index * 10
            elif cell.is_entrance:
                matrix[x][y] = 0.9
            elif cell.is_exit:
                matrix[x][y] = 0.9

    plt.imshow(matrix, cmap="viridis")
    plt.colorbar()
    plt.title("Impulsividad del Supermercado")
    plt.show()