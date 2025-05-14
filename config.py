# Configuración del proyecto
DATA_DIR = "data"
AISLE_INFO_FILENAME = "aisle_info"

LAYOUT_FILE = f"{DATA_DIR}/example_layout.json"
AISLE_INFO_FILE = f"{DATA_DIR}/{AISLE_INFO_FILENAME}.json"
SHOPPING_LISTS_FILE = f"{DATA_DIR}/shopping_lists.json"
TABU_ITERATIONS = 1
TABU_SIZE = 1

# GRID CONFIGURATION
GRID_DIMENSIONS_MULTIPLIER = 1
GRID_DIMENSIONS_PADDING = 12
MAX_AISLE_LENGTH = 10
# AISLE_PRODUCT_COUNT_FILE = f"{DATA_DIR}/aisle_product_count.json"
ADJACENCY_PROBABILITY = 1  # Probability of adjacency between shelves of the same id
LAYOUTS_DIR = "layouts"