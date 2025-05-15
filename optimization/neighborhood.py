from core.grid import SupermarketGrid
from typing import List, Tuple
from copy import deepcopy
import random
from utils.helpers import validate_super_layout

def swap_cells(grid: SupermarketGrid, pos1: Tuple[int, int], pos2: Tuple[int, int]):
    """
    Intercambiar dos estanterías en la cuadrícula.
    :param grid: Cuadrícula a modificar.
    :param pos1: Posición de la primera estantería (fila, columna).
    :param pos2: Posición de la segunda estantería (fila, columna).
    """
    cell_info_1 = grid.grid[pos1[0]][pos1[1]]
    cell_info_2 = grid.grid[pos2[0]][pos2[1]]

    grid.grid[pos1[0]][pos1[1]] = cell_info_2
    grid.grid[pos2[0]][pos2[1]] = cell_info_1

def swap_n_shelves(grid: SupermarketGrid, n: int, overwrite: bool=False, swap_walkable_cells: bool = False):
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

    rows = new_grid.rows
    cols = new_grid.cols

    # Get all valid positions (exclude entrance and exit)
    valid_positions: List[Tuple[int, int]] = []
    for i in range(rows):
        for j in range(cols):
            if new_grid.grid[i][j].is_entrance or new_grid.grid[i][j].is_exit:
                continue
            valid_positions.append((i, j))

    swaps_done = 0
    while swaps_done < n:
        # Randomly select two distinct positions
        pos1, pos2 = random.sample(valid_positions, 2)

        # Get the values at the selected positions
        cell1, cell2 = new_grid.grid[pos1[0]][pos1[1]], new_grid.grid[pos2[0]][pos2[1]]

        # Cannot swap entrance or exit cells
        if cell1.is_entrance or cell1.is_exit or cell2.is_entrance or cell2.is_exit:
            continue

        # Ensure the swap is meaningful (not between two aisles)
        if cell1.is_walkable and cell2.is_walkable:
            continue  # Skip this swap as it's pointless

        if (cell1.is_walkable or cell2.is_walkable) and not swap_walkable_cells: 
            continue

        # Perform the swap
        swap_cells(new_grid, pos1, pos2)

        # Validate the grid after the swap
        if not validate_super_layout(new_grid):
            # If invalid, undo the swap
            swap_cells(new_grid, pos1, pos2)
            # print(f"Intercambio inválido entre {pos1} y {pos2}. Revertido.")
        else:
            # If valid, count the swap
            swaps_done += 1
            # print(f"Intercambio válido entre {pos1} y {pos2}.")

    return new_grid

def gen_neighbors(grid: SupermarketGrid, n: int, swap_amount: int = 20, swap_walkable_cells: bool = False) -> List[SupermarketGrid]:
    """
    Genera n vecinos de la cuadrícula dada.
    :param grid: Cuadrícula a modificar.
    :param n: Número de vecinos a generar.
    :param swap_amount: Número de intercambios por vecino.
    :return: Lista de cuadrículas vecinas.
    """
    neighbors = []
    for _ in range(n):
        neighbor = swap_n_shelves(grid, swap_amount, swap_walkable_cells=swap_walkable_cells)
        neighbors.append(neighbor)
    return neighbors