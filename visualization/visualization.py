from dataclasses import dataclass
import json
import math
import random
from matplotlib.image import AxesImage
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
import numpy as np
import os
import config as cfg
from core.grid import GridInput, SupermarketGrid, GridInput
from typing import List, Dict, Tuple, Set, Optional
from utils.helpers import read_aisle_info, validate_layout
from optimization.neighborhood import swap_n_shelves

def display_layout(layout: SupermarketGrid):
    """
    Desplegar la distribución de la tienda en la consola.
    :param layout: Lista de listas que representa la distribución de la tienda.
    """
    for row in layout.grid:
        for cell in row:
            if cell == 0:
                print("{:^3}".format(" "), end=" ")
            elif cell == -1:
                print("{:^3}".format("X"), end=" ")
            elif cell == -2:
                print("{:^3}".format("C"), end=" ")
            else:
                print("{:^3}".format(cell), end=" ")
        print()

def plot_grid(grid: SupermarketGrid):
    """Visualiza el layout del supermercado"""
    rows = grid.rows
    cols = grid.cols
    matrix = np.zeros((rows, cols))
    
    for x in range(rows):
        for y in range(cols):
            cell = grid.grid[x][y]
            if cell.aisle_id == 0:
                matrix[x][y] = 0.0
            elif cell.is_entrance:
                matrix[x][y] = 1.0
            elif cell.is_exit:
                matrix[x][y] = 2.0
            else:
                matrix[x][y] = 3.0
    
    plt.imshow(matrix, cmap="viridis")
    plt.colorbar()
    plt.title("Distribución de la Tienda")
    plt.show()

def plot_grid_with_ids(grid: SupermarketGrid):
    """
    Visualiza el layout del supermercado con los IDs de las estanterías usando colores personalizados.
    :param grid: La cuadrícula a visualizar.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    generate_individual_plot(grid, ax=ax)
    plt.show()

def plot_grid_difference(grid1: SupermarketGrid, grid2: SupermarketGrid):
    """
    Visualiza las cuadrículas originales y las diferencias entre ellas en la misma figura.
    :param grid1: Primera cuadrícula.
    :param grid2: Segunda cuadrícula.
    """
    rows = grid1.rows
    cols = grid1.cols

    # Create a difference grid
    difference_grid = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            if grid1.grid[i][j] != grid2.grid[i][j]:
                difference_grid[i][j] = 1  # Mark differences with 1
            else:
                difference_grid[i][j] = 0  # Mark no differences with 0

    # Create the figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot grid1 using plot_grid_with_ids
    generate_individual_plot(grid1, ax=axes[0])
    axes[0].set_title("Distribución original")

    # Plot grid2 using plot_grid_with_ids
    generate_individual_plot(grid2, ax=axes[1])
    axes[1].set_title("Distribución modificada")

    # Plot the difference grid
    im = axes[2].imshow(difference_grid, cmap="coolwarm", interpolation="nearest")
    axes[2].set_title("Diferencias (1 = Diferente, 0 = Igual)")
    axes[2].axis("off")

    # Add a colorbar for the difference grid
    cbar = fig.colorbar(im, ax=axes[2], orientation="vertical", fraction=0.046, pad=0.04)
    cbar.set_label("Diferencias")

    plt.tight_layout()
    plt.show()

def plot_multiple_grids(grids: List[SupermarketGrid], names):
    """
    Visualiza múltiples cuadrículas en una sola figura.
    :param grids: Lista de cuadrículas a visualizar.
    """
    num_grids = len(grids)
    fig, axes = plt.subplots(num_grids, 1, figsize=(5, num_grids * 5))

    for i, grid in enumerate(grids):
        generate_individual_plot(grid, ax=axes[i])
        axes[i].set_title(names[i])

    plt.tight_layout()
    plt.show()

def generate_individual_plot(grid: SupermarketGrid, ax=None) -> AxesImage:
    """
    Visualiza el layout del supermercado con los IDs de las estanterías usando colores personalizados.
    :param grid: La cuadrícula a visualizar.
    :param ax: El eje de matplotlib donde se dibujará la cuadrícula. Si es None, se crea una nueva figura.
    """
    rows = grid.rows
    cols = grid.cols
    matrix = np.zeros((rows, cols))
    
    # Define custom colors for specific values
    custom_colors = {
        0: "white",    # Pasillo
    }
    # Generate distinct colors for shelf IDs
    unique_ids = sorted(set(cell.aisle_id for row in grid.grid for cell in row if not cell.is_walkable))
    for i, shelf_id in enumerate(unique_ids):
        color_tuple = plt.get_cmap('tab20')(i % 20)  # Use tab20 for shelf IDs
        custom_colors[shelf_id] = mcolors.to_hex(color_tuple)  # Convert to hex color

    # Create a colormap from the custom colors
    max_value = max(custom_colors.keys())
    color_list = [custom_colors.get(i, "gray") for i in range(max_value + 1)]
    cmap = ListedColormap(color_list)

    # Fill the matrix with the corresponding values
    for x in range(rows):
        for y in range(cols):
            cell = grid.grid[x][y]
            matrix[x][y] = cell.aisle_id
            if cell.is_exit:
                matrix[x][y] = max_value + 1  # Exit
            elif cell.is_entrance:
                matrix[x][y] = max_value + 2

    # Plot on the provided axis or create a new figure
    if ax is None:
        fig, ax = plt.subplots()
        plt.close(fig)  # Close the figure to avoid displaying it immediately
        
    im = ax.imshow(matrix, cmap=cmap, interpolation="nearest")

    # ax.set_title("Distribución de la Tienda")
    ax.axis("off")

    # Overlay IDs on the grid
    for x in range(rows):
        for y in range(cols):
            cell = grid.grid[x][y]
            if not cell.is_walkable:  # Only display IDs for non-pasillo cells
                ax.text(y, x, str(cell.aisle_id), ha="center", va="center", color="black", fontsize=5)

    return im
