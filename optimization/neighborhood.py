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

def swap_n_shelves(grid: SupermarketGrid, n: int, overwrite: bool=False, swap_walkable_cells: bool = False, swap_whole_aisles: bool = False) -> SupermarketGrid:
    """
    Intercambiar n pares de celdas o pasillos enteros en la cuadrícula.
    :param grid: Cuadrícula a modificar.
    :param n: Número de intercambios a realizar.
    :param overwrite: Si es True, modifica la cuadrícula original. Si es False, crea una copia.
    :param swap_walkable_cells: Si es True, permite intercambiar estantería con pasillo.
    :param swap_whole_aisles: Si es True, intercambia pasillos enteros en vez de celdas individuales.
    """
    if overwrite:
        new_grid = grid
    else:
        new_grid = deepcopy(grid)

    rows = new_grid.rows
    cols = new_grid.cols

    if swap_whole_aisles:
        # Get mapping of all cells for each aisle ID
        aisle_cells = {}
        for i in range(rows):
            for j in range(cols):
                cell = new_grid.grid[i][j]
                # Skip entrance, exit, and walkable cells
                if cell.is_entrance or cell.is_exit or cell.is_walkable:
                    continue
                
                # Group cells by aisle ID
                if cell.aisle_id not in aisle_cells:
                    aisle_cells[cell.aisle_id] = []
                aisle_cells[cell.aisle_id].append((i, j))
        
        # Get list of valid aisle IDs that have cells in the grid
        valid_aisle_ids = list(aisle_cells.keys())
        if len(valid_aisle_ids) < 2:
            return new_grid  # Not enough aisles to swap
        
        # Group aisles by their size (number of cells)
        aisles_by_size = {}
        for aisle_id in valid_aisle_ids:
            size = len(aisle_cells[aisle_id])
            if size not in aisles_by_size:
                aisles_by_size[size] = []
            aisles_by_size[size].append(aisle_id)
        
        # Filter to only include sizes with at least 2 aisles (needed for swapping)
        valid_sizes = [size for size, aisles in aisles_by_size.items() if len(aisles) >= 2]
        if not valid_sizes:
            return new_grid  # No aisles of the same size to swap
        
        swaps_done = 0
        max_attempts = n * 10  # Avoid infinite loop
        attempts = 0
        
        while swaps_done < n and attempts < max_attempts:
            attempts += 1
            
            # Randomly select a size that has at least 2 aisles
            if not valid_sizes:
                break  # No more valid sizes to swap
            
            chosen_size = random.choice(valid_sizes)
            aisle_ids_of_size = aisles_by_size[chosen_size]
            
            # Select two different aisles of the same size
            aisle1_id, aisle2_id = random.sample(aisle_ids_of_size, 2)
            
            # Get all cells for both aisles
            aisle1_cells = aisle_cells[aisle1_id]
            aisle2_cells = aisle_cells[aisle2_id]
            
            # Double check that they have the same size
            if len(aisle1_cells) != len(aisle2_cells):
                continue  # Shouldn't happen due to our grouping, but just to be safe
            
            # Make a backup of the grid for validation
            temp_grid = deepcopy(new_grid)
            
            # Swap all cells between the two aisles
            # Strategy: Swap the aisle IDs for all cells in both aisles
            for i, j in aisle1_cells:
                temp_grid.grid[i][j].aisle_id = aisle2_id
                
            for i, j in aisle2_cells:
                temp_grid.grid[i][j].aisle_id = aisle1_id
            
            # Validate the grid after the swap
            if validate_super_layout(temp_grid):
                # If valid, apply the swap to the actual grid

                for i in range(len(aisle1_cells)):
                    swap_cells(new_grid, aisle1_cells[i], aisle2_cells[i])
                
                # Update our tracking of aisle cells
                aisle_cells[aisle1_id], aisle_cells[aisle2_id] = aisle2_cells, aisle1_cells
                
                swaps_done += 1
            
            # If we've tried too many times with this size and failed, remove it
            if attempts % 20 == 0 and swaps_done == 0:
                valid_sizes.remove(chosen_size)
    else:
        # Original cell-by-cell swap implementation
        # Get all valid positions (exclude entrance and exit)
        valid_positions: List[Tuple[int, int]] = []
        for i in range(rows):
            for j in range(cols):
                if new_grid.grid[i][j].is_entrance or new_grid.grid[i][j].is_exit:
                    continue
                valid_positions.append((i, j))

        swaps_done = 0
        max_attempts = n * 10  # Avoid infinite loop
        attempts = 0
        
        while swaps_done < n and attempts < max_attempts:
            attempts += 1
            
            # Randomly select two distinct positions
            pos1, pos2 = random.sample(valid_positions, 2)

            # Get the values at the selected positions
            cell1, cell2 = new_grid.grid[pos1[0]][pos1[1]], new_grid.grid[pos2[0]][pos2[1]]

            # Cannot swap entrance or exit cells
            if cell1.is_entrance or cell1.is_exit or cell2.is_entrance or cell2.is_exit:
                continue

            # Ensure the swap is meaningful (not between two walkable cells)
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
            else:
                # If valid, count the swap
                swaps_done += 1

    return new_grid

def gen_neighbors(grid: SupermarketGrid, n: int, swap_amount: int = 20, swap_walkable_cells: bool = False, swap_whole_aisles: bool = False) -> List[SupermarketGrid]:
    """
    Genera n vecinos de la cuadrícula dada.
    :param grid: Cuadrícula a modificar.
    :param n: Número de vecinos a generar.
    :param swap_amount: Número de intercambios por vecino.
    :param swap_walkable_cells: Si es True, permite intercambiar estantería con pasillo.
    :param swap_whole_aisles: Si es True, intercambia pasillos enteros en vez de celdas individuales.
    :return: Lista de cuadrículas vecinas.
    """
    neighbors = []
    for _ in range(n):
        neighbor = swap_n_shelves(
            grid=grid, 
            n=swap_amount, 
            swap_walkable_cells=swap_walkable_cells,
            swap_whole_aisles=swap_whole_aisles
        )
        neighbors.append(neighbor)
    return neighbors