import json
import networkx as nx

class SupermarketGrid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.aisle_info = {}
        self.entrance = None
        self.exit = None

    @classmethod
    def from_file(cls, layout_filename, impulse_index_filename):
        """
        Carga el layout desde un archivo JSON y la información de impulso desde otro archivo JSON.
        
        Args:
            layout_filename: Ruta al archivo con el layout del supermercado
            impulse_index_filename: Ruta al archivo con los índices de impulso por pasillo
        """
        # Cargar el archivo de layout
        with open(layout_filename, 'r') as f:
            layout_data = json.load(f)
        
        # Cargar el archivo de índices de impulso
        with open(impulse_index_filename, 'r') as f:
            impulse_data = json.load(f)
        
        # Crear la instancia del grid
        grid = cls(layout_data["rows"], layout_data["cols"])
        
        # Inicializar item_to_cells si no existe
        if not hasattr(grid, 'item_to_cells'):
            grid.item_to_cells = {}
        
        # Cargar información de pasillos desde el archivo de impulso
        grid.aisle_info = {}
        for aisle_id, info in impulse_data.items():
            grid.aisle_info[int(aisle_id)] = {
                'impulse_index': info['impulse_index'],
                'name': info['aisle_name']
            }
        
        # Procesar el grid
        for row in range(grid.rows):
            for col in range(grid.cols):
                cell_value = layout_data["grid"][row][col]
                
                # Guardar el valor en el grid
                grid.grid[row][col] = cell_value
                
                # Procesar basado en el tipo de celda
                if cell_value > 0:  # No es un pasillo
                    aisle_id = cell_value
                    # Mapear categoría a celdas
                    if "cells" not in grid.aisle_info[aisle_id]:
                        grid.aisle_info[aisle_id]["cells"] = []
                    grid.aisle_info[aisle_id]["cells"].append((row, col))
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
    def from_dict(cls, data):
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

    def is_connected(self):
        """Verifica que exista un camino entre entrada y salida"""
        if not self.entrance or not self.exit:
            return False
        G = self._build_graph()
        return nx.has_path(G, self.entrance, self.exit)

    def _build_graph(self):
        """
        Construye un grafo de NetworkX a partir del grid.
        Los nodos son las celdas transitables (valor 0, entrada -1, o salida -2).
        Las aristas conectan celdas transitables adyacentes.
        """
        G = nx.Graph()
        
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

    def get_closest_cell(self, current_pos, target_category):
        """Encuentra la celda más cercana de una categoría"""
        if target_category not in self.item_to_cells:
            return None
        candidates = self.item_to_cells[target_category]
        closest = min(
            candidates,
            key=lambda pos: abs(current_pos[0]-pos[0]) + abs(current_pos[1]-pos[1])
        )
        return closest

    def get_path(self, start, end):
        """Calcula la ruta óptima con NetworkX"""
        G = self._build_graph()
        try:
            return nx.shortest_path(G, start, end)
        except nx.NetworkXNoPath:
            return None

    def to_dict(self):
        """Convierte el grid a formato JSON serializable"""
        cells = []
        for x in range(self.rows):
            for y in range(self.cols):
                cell = self.grid[x][y].copy()
                cell["row"] = x
                cell["col"] = y
                cells.append(cell)
        return {
            "rows": self.rows,
            "cols": self.cols,
            "cells": cells
        }