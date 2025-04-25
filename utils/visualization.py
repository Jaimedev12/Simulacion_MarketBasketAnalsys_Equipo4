import matplotlib.pyplot as plt
import numpy as np

def plot_grid(grid):
    """Visualiza el layout del supermercado"""
    rows = grid.rows
    cols = grid.cols
    matrix = np.zeros((rows, cols))
    
    for x in range(rows):
        for y in range(cols):
            cell = grid.grid[x][y]
            if cell["type"] == "shelf":
                matrix[x][y] = cell.get("impulsivity", 0.0)
            elif cell["type"] == "entrance":
                matrix[x][y] = 0.9
            elif cell["type"] == "exit":
                matrix[x][y] = 0.9
    
    plt.imshow(matrix, cmap="viridis")
    plt.colorbar()
    plt.title("Impulsividad del Supermercado")
    plt.show()