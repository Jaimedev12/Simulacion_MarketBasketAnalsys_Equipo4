import json
import math
import random
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg


grid = [
        [
            0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, -2, 0, 0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 5, 5, 5, 0, 0, 7, 7, 7, 0, 0, 9, 9,
            9, 0, 0, 11, 11, 11, 0
        ],
        [
            0, 2, 2, 2, 0, 0, 4, 4, 4, 0, 0, 6, 6, 6, 0, 0, 8, 8, 8, 0, 0, 10,
            10, 10, 0, 0, 12, 12, 12, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 13, 13, 13, 0, 0, 15, 15, 15, 0, 0, 17, 17, 17, 0, 0, 19, 19, 19,
            0, 0, 21, 21, 21, 0, 0, 23, 23, 23, 0
        ],
        [
            0, 14, 14, 14, 0, 0, 16, 16, 16, 0, 0, 18, 18, 18, 0, 0, 20, 20, 20,
            0, 0, 22, 22, 22, 0, 0, 24, 24, 24, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 25, 25, 25, 0, 0, 27, 27, 27, 0, 0, 29, 29, 29, 0, 0, 31, 31, 31,
            0, 0, 33, 33, 33, 0, 0, 35, 35, 35, 0
        ],
        [
            0, 26, 26, 26, 0, 0, 28, 28, 28, 0, 0, 30, 30, 30, 0, 0, 32, 32, 32,
            0, 0, 34, 34, 34, 0, 0, 36, 36, 36, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 37, 37, 37, 0, 0, 39, 39, 39, 0, 0, 41, 41, 41, 0, 0, 43, 43, 43,
            0, 0, 45, 45, 45, 0, 0, 47, 47, 47, 0
        ],
        [
            0, 38, 38, 38, 0, 0, 40, 40, 40, 0, 0, 42, 42, 42, 0, 0, 44, 44, 44,
            0, 0, 46, 46, 46, 0, 0, 48, 48, 48, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 49, 49, 49, 0, 0, 51, 51, 51, 0, 0, 53, 53, 53, 0, 0, 55, 55, 55,
            0, 0, 57, 57, 57, 0, 0, 59, 59, 59, 0
        ],
        [
            0, 50, 50, 50, 0, 0, 52, 52, 52, 0, 0, 54, 54, 54, 0, 0, 56, 56, 56,
            0, 0, 58, 58, 58, 0, 0, 60, 60, 60, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 61, 61, 61, 0, 0, 63, 63, 63, 0, 0, 65, 65, 65, 0, 0, 67, 67, 67,
            0, 0, 69, 69, 69, 0, 0, 71, 71, 71, 0
        ],
        [
            0, 62, 62, 62, 0, 0, 64, 64, 64, 0, 0, 66, 66, 66, 0, 0, 68, 68, 68,
            0, 0, 70, 70, 70, 0, 0, 72, 72, 72, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 73, 73, 73, 0, 0, 75, 75, 75, 0, 0, 77, 77, 77, 0, 0, 79, 79, 79,
            0, 0, 81, 81, 81, 0, 0, 83, 83, 83, 0
        ],
        [
            0, 74, 74, 74, 0, 0, 76, 76, 76, 0, 0, 78, 78, 78, 0, 0, 80, 80, 80,
            0, 0, 82, 82, 82, 0, 0, 84, 84, 84, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 85, 85, 85, 0, 0, 87, 87, 87, 0, 0, 89, 89, 89, 0, 0, 91, 91, 91,
            0, 0, 93, 93, 93, 0, 0, 95, 95, 95, 0
        ],
        [
            0, 86, 86, 86, 0, 0, 88, 88, 88, 0, 0, 90, 90, 90, 0, 0, 92, 92, 92,
            0, 0, 94, 94, 94, 0, 0, 96, 96, 96, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 97, 97, 97, 0, 0, 99, 99, 99, 0, 0, 102, 102, 102, 0, 0, 104,
            104, 104, 0, 0, 106, 106, 106, 0, 0, 108, 108, 108, 0
        ],
        [
            0, 98, 98, 98, 0, 0, 101, 101, 101, 0, 0, 103, 103, 103, 0, 0, 105,
            105, 105, 0, 0, 107, 107, 107, 0, 0, 109, 109, 109, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 110, 110, 110, 0, 0, 112, 112, 112, 0, 0, 114, 114, 114, 0, 0,
            116, 116, 116, 0, 0, 118, 118, 118, 0, 0, 120, 120, 120, 0
        ],
        [
            0, 111, 111, 111, 0, 0, 113, 113, 113, 0, 0, 115, 115, 115, 0, 0,
            117, 117, 117, 0, 0, 119, 119, 119, 0, 0, 121, 121, 121, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 122, 122, 122, 0, 0, 124, 124, 124, 0, 0, 126, 126, 126, 0, 0,
            128, 128, 128, 0, 0, 130, 130, 130, 0, 0, 132, 132, 132, 0
        ],
        [
            0, 123, 123, 123, 0, 0, 125, 125, 125, 0, 0, 127, 127, 127, 0, 0,
            129, 129, 129, 0, 0, 131, 131, 131, 0, 0, 133, 133, 133, 0
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0
        ],
        [
            0, 134, 134, 134, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
    ]

invalid_grid = [
        [ 0, 0, 0, 0, 0],
        [ 0, 1, 1, 1, 0],
        [ 0, 2, 0, 2, 0],
        [ 0, 3, 3, 3, 0],
        [ 0, 0, 0, 0, 0]
    ]

invalid_grid_2 = [
        [ 0, 0, 0, 0, 0],
        [ 0, 1, 1, 1, 0],
        [ 0, 1, 1, 1, 0],
        [ 0, 1, 1, 1, 0],
        [ 0, 0, 0, 0, 0]
    ]

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

def plot_grid_with_ids(grid):
    """Visualiza el layout del supermercado con los IDs de las estanterías usando colores personalizados."""
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
        custom_colors[shelf_id] = plt.cm.tab20(i % 20)  # Use tab20 for shelf IDs

    # Create a colormap from the custom colors
    max_value = max(custom_colors.keys())
    color_list = [custom_colors.get(i, "gray") for i in range(max_value + 1)]
    cmap = ListedColormap(color_list)

    # Fill the matrix with the corresponding values
    for x in range(rows):
        for y in range(cols):
            cell = grid[x][y]
            matrix[x][y] = cell if cell >= 0 else max_value + abs(cell)  # Map negative values to unique indices

    plt.imshow(matrix, cmap=cmap, interpolation="nearest")
    plt.colorbar()
    plt.title("Distribución de la Tienda (con IDs)")

    # Overlay IDs on the grid
    for x in range(rows):
        for y in range(cols):
            cell = grid[x][y]
            if cell != 0:  # Only display IDs for non-pasillo cells
                plt.text(y, x, str(cell), ha="center", va="center", color="black", fontsize=8)

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

    print(f"Grid dimensions: {rows} x {cols}")

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

if __name__ == "__main__":
    grid_attributes = calculate_grid_dimensions()
    
    generate_n_random_grids(1, grid_attributes, True)