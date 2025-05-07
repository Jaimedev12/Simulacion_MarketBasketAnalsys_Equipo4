import json

def load_shopping_lists(filename):
    """Carga listas de compras desde un JSON"""
    with open(filename, 'r') as f:
        return json.load(f)

def save_layout(grid, filename):
    """Guarda el layout en un archivo JSON"""
    with open(filename, 'w') as f:
        json.dump(grid.to_dict(), f, indent=2)