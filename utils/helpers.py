import json
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