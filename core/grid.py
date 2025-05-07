import json
import networkx as nx
from typing import List, Dict, Tuple, Optional, Any, TypedDict

# Define the structure of each aisle info entry
class AisleInfoDict(TypedDict):
    impulse_index: float
    name: str
    cells: List[Tuple[int, int]]

class SupermarketGrid:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows: int = rows
        self.cols: int = cols
        self.grid: List[List[int]] = [[0 for _ in range(cols)] for _ in range(rows)]
        self.aisle_info: Dict[int, AisleInfoDict] = {}
        self.entrance: Optional[Tuple[int, int]] = None
        self.exit: Optional[Tuple[int, int]] = None
        self.item_to_cells: Dict[int, List[Tuple[int, int]]] = {}  # Initialize here

    @classmethod
    def from_file(cls, layout_filename: str, impulse_index_filename: str) -> 'SupermarketGrid':
        """
        Carga el layout desde un archivo JSON y la información de impulso desde otro archivo JSON.
        
        Args:
            layout_filename: Ruta al archivo con el layout del supermercado
            impulse_index_filename: Ruta al archivo con los índices de impulso por pasillo
        """
        # Cargar el archivo de layout
        with open(layout_filename, 'r') as f:
            layout_data: Dict[str, Any] = json.load(f)
        
        # Cargar el archivo de índices de impulso
        with open(impulse_index_filename, 'r') as f:
            impulse_data: Dict[str, Dict[str, Any]] = json.load(f)
        
        # Crear la instancia del grid
        grid: 'SupermarketGrid' = cls(layout_data["rows"], layout_data["cols"])
        
        # Cargar información de pasillos desde el archivo de impulso
        grid.aisle_info = {}
        for aisle_id, info in impulse_data.items():
            grid.aisle_info[int(aisle_id)] = {
                "impulse_index": info['impulse_index'],
                "name": info['aisle_name'],
                "cells": []
            }
        
        # Procesar el grid
        for row in range(grid.rows):
            for col in range(grid.cols):
                cell_value: int = layout_data["grid"][row][col]
                
                # Guardar el valor en el grid
                grid.grid[row][col] = cell_value
                
                # Procesar basado en el tipo de celda
                if cell_value > 0:  # Es un pasillo
                    # Mapear categoría a celdas
                    grid.aisle_info[cell_value]["cells"].append((row, col))
                    
                    # Actualizar item_to_cells para búsqueda rápida
                    if cell_value not in grid.item_to_cells:
                        grid.item_to_cells[cell_value] = []
                    grid.item_to_cells[cell_value].append((row, col))
                elif cell_value == -1:  # Es la entrada
                    grid.entrance = (row, col)
                elif cell_value == -2:  # Es la salida
                    grid.exit = (row, col)
        
        # Utilizar los datos de entrada/salida explícitos si están disponibles
        if "entrance" in layout_data:
            grid.entrance = tuple(layout_data["entrance"])
        if "exit" in layout_data:
            grid.exit = tuple(layout_data["exit"])
        
        # Verificar conectividad
        if not grid.is_connected():
            raise ValueError("El layout no tiene un camino entre entrada y salida")
        
        return grid

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupermarketGrid':
        """Creates a SupermarketGrid from a dictionary representation"""
        grid = cls(data["rows"], data["cols"])
        
        for cell_data in data["cells"]:
            x, y = cell_data["row"], cell_data["col"]
            # Make a copy of the cell data without row/col keys
            cell_copy = {k: v for k, v in cell_data.items() if k not in ["row", "col"]}
            grid.grid[x][y] = cell_copy
            
            if cell_data["type"] == "shelf" and "category" in cell_data:
                category = cell_data["category"]
                if category not in grid.item_to_cells:
                    grid.item_to_cells[category] = []
                grid.item_to_cells[category].append((x, y))
            
            if cell_data["type"] == "entrance":
                grid.entrance = (x, y)
            if cell_data["type"] == "exit":
                grid.exit = (x, y)
        
        print(grid.grid)
        return grid

    def is_connected(self) -> bool:
        """Verifica que exista un camino entre entrada y salida"""
        if not self.entrance or not self.exit:
            return False
        G = self._build_graph()
        return nx.has_path(G, self.entrance, self.exit)

    def _build_graph(self) -> nx.Graph:
        """
        Construye un grafo de NetworkX a partir del grid.
        Los nodos son las celdas transitables (valor 0, entrada -1, o salida -2).
        Las aristas conectan celdas transitables adyacentes.
        """
        G: nx.Graph = nx.Graph()
        
        # Agrega todos los nodos transitables (corredores, entrada, salida)
        for x in range(self.rows):
            for y in range(self.cols):
                cell_value = self.grid[x][y]
                # Considera transitables las celdas con valor 0, -1 (entrada) o -2 (salida)
                if cell_value <= 0:
                    G.add_node((x, y))
        
        # Conecta los nodos adyacentes transitables
        for x in range(self.rows):
            for y in range(self.cols):
                cell_value = self.grid[x][y]
                if cell_value <= 0:  # Si es transitable
                    # Revisar vecinos en las 4 direcciones
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx_pos, ny_pos = x + dx, y + dy
                        # Verificar que está dentro de los límites del grid
                        if 0 <= nx_pos < self.rows and 0 <= ny_pos < self.cols:
                            neighbor_value = self.grid[nx_pos][ny_pos]
                            # Conectar si el vecino también es transitable
                            if neighbor_value <= 0:
                                G.add_edge((x, y), (nx_pos, ny_pos))
        
        return G

    def get_closest_cell(self, current_pos: Tuple[int, int], target_category: int) -> Optional[Tuple[int, int]]:
        """Encuentra la celda más cercana de una categoría"""
        if target_category not in self.item_to_cells:
            return None
        candidates = self.item_to_cells[target_category]
        closest = min(
            candidates,
            key=lambda pos: abs(current_pos[0]-pos[0]) + abs(current_pos[1]-pos[1])
        )
        return closest

    def get_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Calcula la ruta óptima con NetworkX"""
        G = self._build_graph()
        try:
            return nx.shortest_path(G, start, end)
        except nx.NetworkXNoPath:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el grid a formato JSON serializable con la estructura de enteros"""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
            "entrance": self.entrance,
            "exit": self.exit
        }