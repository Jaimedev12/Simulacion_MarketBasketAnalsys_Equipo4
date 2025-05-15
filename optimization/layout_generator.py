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
from visualization.visualization import plot_multiple_grids, plot_grid_difference, plot_grid_with_ids


@dataclass
class GridAttributes:
    shelves_lengths: Dict[int, int]
    rows: int
    cols: int
    entrance_coords: Tuple[int, int]
    exit_coords: Tuple[int, int]
    adjacency_probability: float = 1.0


def calculate_grid_dimensions(adjacency_probability: float = 1) -> GridAttributes:
    """
    Calcular las dimensiones de la cuadrícula con base en la cantidad de
    productos que tiene cada uno. Se utilizará la cantidad de celdas de
    estantería necesarias y se calculará la cantidad de celdas de pasillo
    necesarias para la cuadrícula.
    :param needed_shelves_cells: Cantidad de celdas de estantería necesarias.
    :return: Tupla con las dimensiones de la cuadrícula (x, y).
    """
    # Obtener la cantidad de celdas de pasillo necesarias
    aisle_lengths, needed_shelves_cells = calculate_aisle_length()

    multiplier = cfg.GRID_DIMENSIONS_MULTIPLIER
    padding = cfg.GRID_DIMENSIONS_PADDING
    cols = math.ceil(math.sqrt(needed_shelves_cells))
    rows = math.ceil(needed_shelves_cells / cols) 

    # Aumentar las dimensiones de la cuadrícula para incluir pasillos
    rows = padding + rows * multiplier
    cols = padding + cols * multiplier

    # print(f"Grid dimensions: {rows} x {cols}")

    # Place the entrance and exit both in the first row, one in the first
    # quarter and the other in the last quarter of the row 
    entrance_coords = (0, cols // 4)
    exit_coords = (0, cols * 3 // 4)

    return GridAttributes(
        shelves_lengths=aisle_lengths,
        rows=rows,
        cols=cols,
        entrance_coords=entrance_coords,
        exit_coords=exit_coords,
        adjacency_probability=adjacency_probability
    )

def calculate_aisle_length(max_aisle_length: int = 10) -> Tuple[Dict[int, int], int]:
    """
    Calcular la longitud de los pasillos con base en la cantidad de productos
    que tiene cada uno. Se utilizará la longitud máxima de pasillo en la
    configuración y a partir de ahí se calculará la longitud de cada pasillo.
    :return: Diccionario con la longitud de cada pasillo y la cantidad de
    celdas necesarias.
    """

    aisle_info = read_aisle_info()

    # Calcular la longitud de cada pasillo
    shelves_lengths: Dict[int, int] = {}
    needed_cells = 0
    max_product_count = 0
    for aisle_id, product_info in aisle_info.items():
        p_count = product_info.product_count
        if p_count > max_product_count:
            max_product_count = p_count

    for aisle_id, product_info in aisle_info.items():
        p_count = product_info.product_count
        if p_count > 0:
            aisle_length = math.ceil(max_aisle_length * (p_count / max_product_count))
            shelves_lengths[aisle_id] = aisle_length
            needed_cells += aisle_length
        else:
            shelves_lengths[aisle_id] = 0
    
    return shelves_lengths, needed_cells

def place_shelf_recursively(
        grid: List[List[int]], 
        available_positions: Set[Tuple[int, int]], 
        aisle_id: int, 
        placed: int, 
        length: int, 
        adjacency_prob: float, 
        position: Optional[Tuple[int, int]]=None
        ):
    """
    Recursive function to place shelves in the grid.
    :param grid: The grid where shelves are being placed.
    :param available_positions: List of available positions.
    :param aisle_id: The ID of the aisle being placed.
    :param placed: Number of shelves already placed for this aisle.
    :param length: Total number of shelves to place for this aisle.
    :param adjacency_prob: Probability of placing an adjacent shelf.
    :param position: Specific position to place the shelf (row, col). If None, a random position is selected.
    :return: Updated number of shelves placed.
    """
    if placed >= length or len(available_positions) == 0:
        return placed

    if position:
        # Use the provided position
        row, col = position
    else:
        row, col = random.choice(list(available_positions))

    # Validate the position
    grid[row][col] = int(aisle_id)
    if not validate_layout(grid):
        grid[row][col] = 0  # Reset the position if invalid
        if position:
            return placed  # Return without placing if a specific position was invalid
        else:
            # If no specific position was provided, try another random position
            return place_shelf_recursively(grid, available_positions, aisle_id, placed, length, adjacency_prob)

    # If valid, mark the position as occupied
    available_positions.remove((row, col))  # Remove the used position
    placed += 1

    # Attempt to place adjacent shelves based on adjacency probability
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        if random.random() < adjacency_prob:
            adj_row, adj_col = row + dx, col + dy
            if (adj_row, adj_col) in available_positions:
                placed = place_shelf_recursively(
                    grid, available_positions, aisle_id, placed, length, adjacency_prob, position=(adj_row, adj_col)
                )
                if placed >= length:
                    break

    if placed < length:
        placed = place_shelf_recursively(
            grid, available_positions, aisle_id, placed, length, adjacency_prob
        )

    return placed

def generate_random_grid(grid_attributes: GridAttributes) -> SupermarketGrid:
    """
    Generar una cuadrícula aleatoria con pasillos y estanterías. Las estanterías
    tienen que tener la longitud de casillas especificada por shelves_lengths.
    Sin embargo, las cuadrículas de una misma estantería podrían estar
    separadas, es decir, no necesariamente serán contiguas.
    :param grid_attributes: Atributos de la cuadrícula (dimensiones, entrada, salida).
    :return: Cuadrícula generada aleatoriamente.
    """
    shelves_lengths = grid_attributes.shelves_lengths
    rows = grid_attributes.rows
    cols = grid_attributes.cols
    entrance_coords = grid_attributes.entrance_coords
    exit_coords = grid_attributes.exit_coords
    adjacency_prob = grid_attributes.adjacency_probability

    grid: List[List[int]] = [[0] * cols for _ in range(rows)]
    
    # Colocar la entrada y salida
    # grid[entrance_coords[0]][entrance_coords[1]] = -2  # Entrada
    # grid[exit_coords[0]][exit_coords[1]] = -1  # Salida

    # Colocar estanterías
    available_positions: Set[Tuple[int, int]] = set()

    for row in range(rows):
        for col in range(cols):
            pos = (row, col)
            if not grid[row][col] == 0:
                continue
            if pos == entrance_coords or pos == exit_coords:
                continue
                
            available_positions.add((row, col))
    
    for aisle_id, length in shelves_lengths.items():
        if length > 0:
            placed = 0
            placed = place_shelf_recursively(grid, available_positions, aisle_id, placed, length, adjacency_prob)

    grid_input = GridInput(
        rows=rows,
        cols=cols,
        grid=grid,
        entrance=entrance_coords,
        exit=exit_coords,
    )

    return SupermarketGrid.from_dict(grid_input)

def save_grid_to_json(grid: SupermarketGrid, filename: str, grid_attributes: GridAttributes):
    """
    Guardar la cuadrícula en un archivo JSON.
    :param grid: Cuadrícula a guardar.
    :param filename: Nombre del archivo JSON.
    :param grid_attributes: Atributos de la cuadrícula (dimensiones, entrada, salida).
    """
    # Asegurarse que el directorio layouts existe
    if not os.path.exists(cfg.LAYOUTS_DIR):
        os.makedirs(cfg.LAYOUTS_DIR)
        
    with open(os.path.join(cfg.LAYOUTS_DIR, filename), 'w') as file:
        json.dump({
            "grid": grid.grid,
            "rows": grid_attributes.rows,
            "cols": grid_attributes.cols,
            "entrance": grid_attributes.entrance_coords,
            "exit": grid_attributes.exit_coords,
        }, file, indent=4)

def generate_n_random_grids(n: int, grid_attributes: GridAttributes, should_plot: bool=False):
    """
    Generar n cuadrículas aleatorias y guardarlas en archivos JSON.
    :param n: Número de cuadrículas a generar.
    :param grid_attributes: Atributos de la cuadrícula (dimensiones, entrada, salida).
    """
    for i in range(n):
        grid = generate_random_grid(grid_attributes)
        filename = f"grid_{i}.json"
        save_grid_to_json(grid, filename, grid_attributes)
        print(f"Grid {i} saved to {filename}")
        if should_plot:
            plot_grid_with_ids(grid)

def get_grid_object(adjacency_probability: float = 1) -> SupermarketGrid:
    """
    Obtener la cuadrícula generada a partir de los atributos de la cuadrícula.
    :return: Cuadrícula generada.
    """
    grid_attributes = calculate_grid_dimensions()

    grid = generate_random_grid(grid_attributes)

    return grid

if __name__ == "__main__":
    
    # generate_n_random_grids(1, grid_attributes, True)
    # grid = generate_random_grid(grid_attributes)
    # plot_grid_with_ids(grid)
    # grid_2 = swap_n_shelves(grid, 50)
    # plot_grid_with_ids(grid_2)
    # plot_grid_difference(grid, grid_2)

    adjacency_probability = 1.0
    grid_attributes = calculate_grid_dimensions(adjacency_probability)
    grids = []
    names = []
    for i in range(2):
        names.append(f"Probabilidad de adyacencia: {grid_attributes.adjacency_probability}")
        grid = generate_random_grid(grid_attributes)
        grids.append(grid)
        grid_attributes.adjacency_probability = 0
    plot_multiple_grids(grids, names)
    changed_grid = swap_n_shelves(grids[0], 20)
    plot_grid_difference(grids[0], changed_grid)
    
