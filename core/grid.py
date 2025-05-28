from dataclasses import dataclass
import json
import networkx as nx
from typing import List, Dict, Tuple, Optional, Any, TypedDict
import config as cfg

# Define the structure of each aisle info entry
@dataclass
class AisleInfo():
    impulse_index: float
    name: str
    product_count: int
    cells: List[Tuple[int, int]]

@dataclass
class CellInfo():
    is_walkable: bool  # True si es un pasillo, False si es un estante
    aisle_id: int  # Puede ser None si no es un pasillo
    product_id_range: Tuple[int, int]
    is_exit: bool = False
    is_entrance: bool = False

@dataclass
class GridInput():
    rows: int
    cols: int
    grid: List[List[int]]
    entrance: Tuple[int, int]
    exit: Tuple[int, int]

class SupermarketGrid:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows: int = rows
        self.cols: int = cols
        self.grid: List[List[CellInfo]] = [
                [
                    CellInfo(is_walkable=True, aisle_id=0, product_id_range=(0, 0)) 
                    for _ in range(cols)
                ] for _ in range(rows)
            ]
        self.aisle_info: Dict[int, AisleInfo] = {}
        self.entrance: Tuple[int, int] = (0, 0)
        self.exit: Tuple[int, int] = (0, 0)
        self.graph: nx.Graph

    @classmethod
    def read_aisle_info(cls, aisle_info_filename: str) -> Dict[int, AisleInfo]:
        """
        Carga la información de los pasillos desde un archivo JSON.
        
        Args:
            aisle_info_filename: Ruta al archivo con la información de los pasillos.
        
        Returns:
            Dict[int, AisleInfo]: Un diccionario con la información de los pasillos.
        """
        with open(aisle_info_filename, 'r') as f:
            aisle_info_from_file: Dict[str, Dict[str, Any]] = json.load(f)
            aisle_info: Dict[int, AisleInfo] = {}

            for aisle_id_str, info in aisle_info_from_file.items():
                aisle_id = int(aisle_id_str)
                aisle_info[int(aisle_id)] = AisleInfo(impulse_index=info['impulse_index'],
                    name=info['aisle_name'], product_count=info['product_count'], cells=[])
                
            return aisle_info

    @classmethod
    def from_dict(cls, layout_data: GridInput, aisle_info_file: str = cfg.AISLE_INFO_FILE) -> 'SupermarketGrid':
        """
        Crea una instancia de SupermarketGrid a partir de un diccionario.
        
        Args:
            grid_data: Un diccionario que contiene la información del grid.
        
        Returns:
            SupermarketGrid: La instancia creada.
        """
        
        # Crear la instancia del grid
        grid: 'SupermarketGrid' = cls(layout_data.rows, layout_data.cols)
        
        # Cargar información de pasillos desde el archivo de impulso
        aisle_info = cls.read_aisle_info(aisle_info_file)
        grid.aisle_info = aisle_info
        
        # Procesar el grid
        for row in range(grid.rows):
            for col in range(grid.cols):
                aisle_id: int = layout_data.grid[row][col]
                
                grid.grid[row][col].is_walkable = (aisle_id <= 0)  # True si es un pasillo o entrada/salida
                grid.grid[row][col].aisle_id = aisle_id

                # Procesar basado en el tipo de celda
                if aisle_id > 0:  # Es un pasillo
                    # Mapear categoría a celdas
                    grid.aisle_info[aisle_id].cells.append((row, col))
        
        # Utilizar los datos de entrada/salida explícitos si están disponibles
        grid.entrance = layout_data.entrance
        grid.exit = layout_data.exit
        grid.grid[grid.exit[0]][grid.exit[1]].is_exit = True
        grid.grid[grid.entrance[0]][grid.entrance[1]].is_entrance = True
        
        # Verificar conectividad
        # if not grid.is_connected():
        #     raise ValueError("El layout no tiene un camino entre entrada y salida")
        
        # Llenar rangos de ids de productos
        for aisle_id, info in grid.aisle_info.items():

            if (len(info.cells) == 0 or info.product_count == 0):
                continue

            step_size = info.product_count // len(info.cells) if info.product_count > 0 else 0
            for i, coord in enumerate(info.cells):
                row, col = coord
                cell_info = grid.grid[row][col]
                # Asignar el rango de ids de productos a la celda
                start = i * step_size
                end = start + step_size if i < len(info.cells) - 1 else info.product_count+1
                cell_info.product_id_range = (start, end)
    
        cls._build_graph(grid)

        return grid

    @classmethod
    def from_file(cls, layout_filename: str, aisle_info_filename: str) -> 'SupermarketGrid':
        """
        Carga el layout desde un archivo JSON y la información de impulso desde otro archivo JSON.
        
        Args:
            layout_filename: Ruta al archivo con el layout del supermercado
            aisle_info_filename: Ruta al archivo con la info de los pasillos
        """
        # Cargar el archivo de layout
        with open(layout_filename, 'r') as f:
            layout_data: Dict[str, Any] = json.load(f)
        
        grid_info: GridInput = GridInput(
            rows=layout_data['rows'],
            cols=layout_data['cols'],
            grid=layout_data['grid'],
            entrance=tuple(layout_data['entrance']),
            exit=tuple(layout_data['exit'])
        )
       
        return cls.from_dict(grid_info, aisle_info_filename)

    def is_connected(self) -> bool:
        """Verifica que exista un camino entre entrada y salida"""
        if not self.entrance or not self.exit:
            return False
        return nx.has_path(self.graph, self.entrance, self.exit)

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
                cell = self.grid[x][y]
                # Considera transitables las celdas con valor 0, -1 (entrada) o -2 (salida)
                if cell.is_walkable:
                    G.add_node((x, y))
        
        # Conecta los nodos adyacentes transitables
        for x in range(self.rows):
            for y in range(self.cols):
                cell = self.grid[x][y]
                if cell.is_walkable:  # Si es transitable
                    # Revisar vecinos en las 4 direcciones
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx_pos, ny_pos = x + dx, y + dy
                        # Verificar que está dentro de los límites del grid
                        if 0 <= nx_pos < self.rows and 0 <= ny_pos < self.cols:
                            neighbor_cell = self.grid[nx_pos][ny_pos]
                            # Conectar si el vecino también es transitable
                            if neighbor_cell.is_walkable:
                                G.add_edge((x, y), (nx_pos, ny_pos))
        
        self.graph = G  # Guardar el grafo en la instancia
        return G

    def get_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Calcula la ruta óptima con NetworkX"""
        G = self.graph

        if start not in G or end not in G:
            return None

        try:
            return list(nx.shortest_path(G, start, end))
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