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


@dataclass
class GridAttributes:
    shelves_lengths: Dict[int, int]
    rows: int
    cols: int
    entrance_coords: Tuple[int, int]
    exit_coords: Tuple[int, int]


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

# def validate_layout(layout: SupermarketGrid):
#     # Recorrer desde una casilla de pasillo para validar que se pueda llegar a
#     # todas las demás casillas de pasillo
#     rows = layout.rows
#     cols = layout.cols
#     visited_aisle = [[False] * cols for _ in range(rows)]
#     visited_shelves = [[False] * cols for _ in range(rows)]
#     queue = []
    
#     for i in range(rows):
#         for j in range(cols):
#             if layout.grid[i][j].is_walkable:
#                 queue.append((i, j))
#                 visited_aisle[i][j] = True
#                 break
#         if queue:
#             break
#     if not queue:
#         return False
    
#     # Realizar búsqueda en anchura (BFS) para marcar todas las casillas de
#     # pasillo alcanzables
#     while queue:
#         x, y = queue.pop(0)
#         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < rows and 0 <= ny < cols and not visited_aisle[nx][ny] and layout.grid[nx][ny].is_walkable:
#                 visited_aisle[nx][ny] = True
#                 queue.append((nx, ny))
#             elif 0 <= nx < rows and 0 <= ny < cols and not visited_shelves[nx][ny] and not layout.grid[nx][ny].is_walkable:
#                 visited_shelves[nx][ny] = True
    
#     # Verificar que no haya celdas de pasillo no alcanzadas
#     for i in range(rows):
#         for j in range(cols):
#             if layout.grid[i][j].is_walkable and not visited_aisle[i][j]:
#                 return False
    
#     # Verificar que todas las casillas de pasillo sean alcanzables
#     for i in range(rows):
#         for j in range(cols):
#             if layout.grid[i][j].aisle_id > 0 and not visited_shelves[i][j]:
#                 return False
    
#     return True

def calculate_grid_dimensions() -> GridAttributes:
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
        exit_coords=exit_coords
    )

def calculate_aisle_length() -> Tuple[Dict[int, int], int]:
    """
    Calcular la longitud de los pasillos con base en la cantidad de productos
    que tiene cada uno. Se utilizará la longitud máxima de pasillo en la
    configuración y a partir de ahí se calculará la longitud de cada pasillo.
    :return: Diccionario con la longitud de cada pasillo y la cantidad de
    celdas necesarias.
    """
    # Obtenemos la longitud máxima de pasillo de la configuración
    max_aisle_length = cfg.MAX_AISLE_LENGTH

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


    
    grid: List[List[int]] = [[0] * cols for _ in range(rows)]
    
    # Probabilidad de que cuando se coloque una estantería de un tipo, se
    # coloque otra estantería de ese mismo tipo al lado en vez de en una
    # posición aleatoria
    print(cfg.ADJACENCY_PROBABILITY)
    adjacency_prob = cfg.ADJACENCY_PROBABILITY

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

def get_grid_object() -> SupermarketGrid:
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

    cfg.ADJACENCY_PROBABILITY = 1.0
    grid_attributes = calculate_grid_dimensions()
    grids = []
    names = []
    for i in range(2):
        names.append(f"Probabilidad de adyacencia: {cfg.ADJACENCY_PROBABILITY}")
        grid = generate_random_grid(grid_attributes)
        grids.append(grid)
        cfg.ADJACENCY_PROBABILITY -= 1
    plot_multiple_grids(grids, names)
    changed_grid = swap_n_shelves(grids[0], 20)
    plot_grid_difference(grids[0], changed_grid)
    
