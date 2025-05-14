import json
from operator import le
from typing import Dict, List, Tuple
from core.grid import SupermarketGrid, AisleInfo, CellInfo
import config as cfg

def load_shopping_lists(filename):
    """Carga listas de compras desde un JSON"""
    with open(filename, 'r') as f:
        return json.load(f)

def save_layout(grid, filename):
    """Guarda el layout en un archivo JSON"""
    with open(filename, 'w') as f:
        json.dump(grid.to_dict(), f, indent=2)

def read_aisle_info() -> Dict[int, AisleInfo]:
    """Carga la información de los pasillos desde un JSON"""
    with open(cfg.AISLE_INFO_FILE, 'r') as f:
        aisle_info_raw = json.load(f)

    aisle_info: Dict[int, AisleInfo] = {}
    for aisle_id_str, info in aisle_info_raw.items():
        aisle_id = int(aisle_id_str)
        aisle_info[aisle_id] = AisleInfo(
            impulse_index=info['impulse_index'],
            name=info['aisle_name'],
            product_count=info['product_count'],
            cells=[]
        )
    return aisle_info

def validate_layout(layout: List[List[int]]):
    # Recorrer desde una casilla de pasillo para validar que se pueda llegar a
    # todas las demás casillas de pasillo
    rows = len(layout)
    cols = len(layout[0]) if rows > 0 else 0
    visited_aisle = [[False] * cols for _ in range(rows)]
    visited_shelves = [[False] * cols for _ in range(rows)]
    queue = []
    
    for i in range(rows):
        for j in range(cols):
            if layout[i][j] == 0:
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
            if 0 <= nx < rows and 0 <= ny < cols and not visited_aisle[nx][ny] and layout[nx][ny] == 0:
                visited_aisle[nx][ny] = True
                queue.append((nx, ny))
            elif 0 <= nx < rows and 0 <= ny < cols and not visited_shelves[nx][ny] and not layout[nx][ny] == 0:
                visited_shelves[nx][ny] = True
    
    # Verificar que no haya celdas de pasillo no alcanzadas
    for i in range(rows):
        for j in range(cols):
            if layout[i][j] == 0 and not visited_aisle[i][j]:
                return False
    
    # Verificar que todas las casillas de pasillo sean alcanzables
    for i in range(rows):
        for j in range(cols):
            if layout[i][j] > 0 and not visited_shelves[i][j]:
                return False
    
    return True

def validate_super_layout(layout: SupermarketGrid):
    value_grid = [[cell.aisle_id for cell in row] for row in layout.grid]
    if not validate_layout(value_grid):
        return False
    return True