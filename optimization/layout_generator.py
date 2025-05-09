import json
import math
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
from copy import deepcopy
from core.grid import GridInput, SupermarketGrid


def display_layout(layout):
    """
    Desplegar la distribución de la tienda en la consola.
    :param layout: Lista de listas que representa la distribución de la tienda.
    """
    for row in layout:
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

def plot_grid(grid):
    """Visualiza el layout del supermercado"""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    matrix = np.zeros((rows, cols))
    
    for x in range(rows):
        for y in range(cols):
            cell = grid[x][y]
            if cell == 0:
                matrix[x][y] = 0.0
            elif cell == -1:
                matrix[x][y] = 1.0
            elif cell == -2:
                matrix[x][y] = 2.0
            else:
                matrix[x][y] = 3.0
    
    plt.imshow(matrix, cmap="viridis")
    plt.colorbar()
    plt.title("Distribución de la Tienda")
    plt.show()

def generate_individual_plot(grid, ax=None):
    """
    Visualiza el layout del supermercado con los IDs de las estanterías usando colores personalizados.
    :param grid: La cuadrícula a visualizar.
    :param ax: El eje de matplotlib donde se dibujará la cuadrícula. Si es None, se crea una nueva figura.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    matrix = np.zeros((rows, cols))
    
    # Define custom colors for specific values
    custom_colors = {
        0: "white",    # Pasillo
        -1: "red",     # Salida
        -2: "green",   # Entrada
    }
    # Generate distinct colors for shelf IDs
    unique_ids = sorted(set(cell for row in grid for cell in row if cell > 0))
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
            cell = grid[x][y]
            matrix[x][y] = cell if cell >= 0 else max_value + abs(cell)  # Map negative values to unique indices

    # Plot on the provided axis or create a new figure
    if ax is None:
        fig, ax = plt.subplots()
    im = ax.imshow(matrix, cmap=cmap, interpolation="nearest")
    ax.set_title("Distribución de la Tienda (con IDs)")
    ax.axis("off")

    # Overlay IDs on the grid
    for x in range(rows):
        for y in range(cols):
            cell = grid[x][y]
            if cell != 0:  # Only display IDs for non-pasillo cells
                ax.text(y, x, str(cell), ha="center", va="center", color="black", fontsize=8)

    return im

def plot_grid_with_ids(grid):
    """
    Visualiza el layout del supermercado con los IDs de las estanterías usando colores personalizados.
    :param grid: La cuadrícula a visualizar.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    generate_individual_plot(grid, ax=ax)
    plt.show()

def plot_grid_difference(grid1, grid2):
    """
    Visualiza las cuadrículas originales y las diferencias entre ellas en la misma figura.
    :param grid1: Primera cuadrícula.
    :param grid2: Segunda cuadrícula.
    """
    rows = len(grid1)
    cols = len(grid1[0]) if rows > 0 else 0

    # Create a difference grid
    difference_grid = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            if grid1[i][j] != grid2[i][j]:
                difference_grid[i][j] = 1  # Mark differences with 1
            else:
                difference_grid[i][j] = 0  # Mark no differences with 0

    # Create the figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot grid1 using plot_grid_with_ids
    generate_individual_plot(grid1, ax=axes[0])
    axes[0].set_title("Grid 1 (Original)")

    # Plot grid2 using plot_grid_with_ids
    generate_individual_plot(grid2, ax=axes[1])
    axes[1].set_title("Grid 2 (Modified)")

    # Plot the difference grid
    im = axes[2].imshow(difference_grid, cmap="coolwarm", interpolation="nearest")
    axes[2].set_title("Diferencias (1 = Diferente, 0 = Igual)")
    axes[2].axis("off")

    # Add a colorbar for the difference grid
    cbar = fig.colorbar(im, ax=axes[2], orientation="vertical", fraction=0.046, pad=0.04)
    cbar.set_label("Diferencias")

    plt.tight_layout()
    plt.show()

def validate_layout(layout):
    """
    Validar la distribución de la tienda.
    :param layout: Lista de listas que representa la distribución de la tienda.
    :return: True si la distribución es válida, False en caso contrario.
    """
    # Recorrer desde una casilla de pasillo para validar que se pueda llegar a
    # todas las demás casillas de pasillo
    rows = len(layout)
    cols = len(layout[0]) if rows > 0 else 0
    visited_aisle = [[False] * cols for _ in range(rows)]
    visited_shelves = [[False] * cols for _ in range(rows)]
    queue = []
    # Encontrar la casilla de entrada (-2) o la primera casilla de pasillo (0)
    for i in range(rows):
        for j in range(cols):
            if layout[i][j] in [0, -2]:
                queue.append((i, j))
                visited_aisle[i][j] = True
                break
        if queue:
            break
    if not queue:
        return False
    
    # Realizar búsqueda en anchura (BFS) para marcar todas las casillas de
    # pasillo alcanzables
    while queue:
        x, y = queue.pop(0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and not visited_aisle[nx][ny] and layout[nx][ny] in [0, -2, -1]:
                visited_aisle[nx][ny] = True
                queue.append((nx, ny))
            elif 0 <= nx < rows and 0 <= ny < cols and not visited_shelves[nx][ny] and layout[nx][ny] > 0:
                visited_shelves[nx][ny] = True
    
    # Verificar que no haya celdas de pasillo no alcanzadas
    for i in range(rows):
        for j in range(cols):
            if layout[i][j] in [-2, -1, 0] and not visited_aisle[i][j]:
                return False
    
    # Verificar que todas las casillas de pasillo sean alcanzables
    for i in range(rows):
        for j in range(cols):
            if layout[i][j] > 0 and not visited_shelves[i][j]:
                return False
    
    return True

def calculate_grid_dimensions():
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

    return {"dimensions": (rows, cols), "aisle_lengths": aisle_lengths, "entrance_coords": entrance_coords, "exit_coords": exit_coords}

def calculate_aisle_length():
    """
    Calcular la longitud de los pasillos con base en la cantidad de productos
    que tiene cada uno. Se utilizará la longitud máxima de pasillo en la
    configuración y a partir de ahí se calculará la longitud de cada pasillo.
    :return: Diccionario con la longitud de cada pasillo y la cantidad de
    celdas necesarias.
    """
    # Obtenemos la longitud máxima de pasillo de la configuración
    max_aisle_length = cfg.MAX_AISLE_LENGTH
    # Obtener pasillos con su cantidad de productos de aisle_product_count.json
    aisle_product_count_filename = cfg.AISLE_PRODUCT_COUNT_FILE
    aisle_product_count = {}
    with open(aisle_product_count_filename, 'r') as file:
        aisle_product_count = json.load(file)

    # Calcular la longitud de cada pasillo
    shelves_lengths = {}
    needed_cells = 0
    for aisle_id, product_count in aisle_product_count.items():
        if product_count > 0:
            aisle_length = math.ceil(max_aisle_length * (product_count / max(aisle_product_count.values())))
            shelves_lengths[aisle_id] = aisle_length
            needed_cells += aisle_length
        else:
            shelves_lengths[aisle_id] = 0
    
    return shelves_lengths, needed_cells

def place_shelf_recursively(grid, available_positions, aisle_id, placed, length, adjacency_prob, position=None):
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
    if placed >= length or not available_positions:
        return placed

    if position:
        # Use the provided position
        row, col = position
    else:
        # Choose a random position from available positions
        row, col = random.choice(available_positions)

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

def generate_random_grid(grid_attributes):
    """
    Generar una cuadrícula aleatoria con pasillos y estanterías. Las estanterías
    tienen que tener la longitud de casillas especificada por shelves_lengths.
    Sin embargo, las cuadrículas de una misma estantería podrían estar
    separadas, es decir, no necesariamente serán contiguas.
    :param grid_attributes: Atributos de la cuadrícula (dimensiones, entrada, salida).
    :return: Cuadrícula generada aleatoriamente.
    """
    shelves_lengths = grid_attributes["aisle_lengths"]
    dimensions = grid_attributes["dimensions"]
    entrance_coords = grid_attributes["entrance_coords"]
    exit_coords = grid_attributes["exit_coords"]

    rows, cols = dimensions
    grid = [[0] * cols for _ in range(rows)]
    # Probabilidad de que cuando se coloque una estantería de un tipo, se
    # coloque otra estantería de ese mismo tipo al lado en vez de en una
    # posición aleatoria
    adjacency_prob = cfg.ADJACENCY_PROBABILITY

    # Colocar la entrada y salida
    grid[entrance_coords[0]][entrance_coords[1]] = -2  # Entrada
    grid[exit_coords[0]][exit_coords[1]] = -1  # Salida

    # Colocar estanterías
    available_positions = [(row, col) for row in range(rows) for col in range(cols) if grid[row][col] == 0]
    
    for aisle_id, length in shelves_lengths.items():
        if length > 0:
            placed = 0
            placed = place_shelf_recursively(grid, available_positions, aisle_id, placed, length, adjacency_prob)

    # Colocar pasillos (0) en las celdas vacías
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 0:
                grid[i][j] = 0
    
    return grid

def save_grid_to_json(grid, filename, grid_attributes):
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
            "grid": grid,
            "rows": grid_attributes["dimensions"][0],
            "cols": grid_attributes["dimensions"][1],
            "entrance": grid_attributes["entrance_coords"],
            "exit": grid_attributes["exit_coords"],
        }, file, indent=4)

def swap_n_shelves(grid, n, overwrite=False):
    """
    Intercambiar n pares de celdas en la cuadrícula. El intercambio puede ser entre:
    - Dos estanterías.
    - Una estantería y un pasillo.
    No se permite intercambiar la entrada, la salida, ni dos pasillos.
    Si un intercambio no es válido, no se cuenta como uno de los n intercambios.
    :param grid: Cuadrícula a modificar.
    :param n: Número de intercambios a realizar.
    """
    if overwrite:
        new_grid = grid
    else:
        new_grid = deepcopy(grid)

    rows = len(new_grid)
    cols = len(new_grid[0]) if rows > 0 else 0

    # Get all valid positions (exclude entrance and exit)
    valid_positions = [(i, j) for i in range(rows) for j in range(cols) if new_grid[i][j] != -1 and new_grid[i][j] != -2]

    swaps_done = 0
    while swaps_done < n:
        # Randomly select two distinct positions
        pos1, pos2 = random.sample(valid_positions, 2)

        # Get the values at the selected positions
        val1, val2 = new_grid[pos1[0]][pos1[1]], new_grid[pos2[0]][pos2[1]]

        # Ensure the swap is meaningful (not between two aisles)
        if val1 == 0 and val2 == 0:
            continue  # Skip this swap as it's pointless

        # Perform the swap
        new_grid[pos1[0]][pos1[1]], new_grid[pos2[0]][pos2[1]] = val2, val1

        # Validate the grid after the swap
        if not validate_layout(new_grid):
            # If invalid, undo the swap
            new_grid[pos1[0]][pos1[1]], new_grid[pos2[0]][pos2[1]] = val1, val2
            # print(f"Intercambio inválido entre {pos1} y {pos2}. Revertido.")
        else:
            # If valid, count the swap
            swaps_done += 1
            # print(f"Intercambio válido entre {pos1} y {pos2}.")

    return new_grid

def generate_n_random_grids(n, grid_attributes, should_plot=False):
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

def get_grid_object(aisle_info_filename: str) -> SupermarketGrid:
    """
    Obtener la cuadrícula generada a partir de los atributos de la cuadrícula.
    :return: Cuadrícula generada.
    """
    grid_attributes = calculate_grid_dimensions()

    grid = generate_random_grid(grid_attributes)

    # Quitar la entrada y salida de la representacion
    grid[grid_attributes["entrance_coords"][0]][grid_attributes["entrance_coords"][1]] = 0  # Entrance
    grid[grid_attributes["exit_coords"][0]][grid_attributes["exit_coords"][1]] = 0  # Exit

    grid_input: GridInput = GridInput(
        rows=grid_attributes["dimensions"][0],
        cols=grid_attributes["dimensions"][1],
        grid=grid,
        entrance=grid_attributes["entrance_coords"],
        exit=grid_attributes["exit_coords"],
    )

    return SupermarketGrid.from_dict(grid_input, aisle_info_filename)

if __name__ == "__main__":
    # grid_attributes = calculate_grid_dimensions()

    print(get_grid_object("../data/aisle_product_count.json"))
    
    # generate_n_random_grids(1, grid_attributes, True)
    # grid = generate_random_grid(grid_attributes)
    # plot_grid_with_ids(grid)
    # grid_2 = swap_n_shelves(grid, 50)
    # plot_grid_with_ids(grid_2)
    # plot_grid_difference(grid, grid_2)
