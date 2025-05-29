import json
import numpy as np
from core.grid import SupermarketGrid, GridInput
import config as cfg
import math


def gen_category_layout() -> SupermarketGrid:
    """
    Generate a supermarket layout grouping aisles by category.
    Categories are placed in blocks, filling from top to bottom, left to right.
    """
    categorized = separate_by_category()  # Uses your function

    # Define the order in which categories will appear in the layout
    category_order = [
        "food",
        "beverages",
        "special diet",
        "condiments",
        "household",
        "personal care",
        "pet",
        "baby",
        "other",
    ]

    rows = 36
    cols = 35
    grid = np.zeros((rows, cols), dtype=int)
    grid[0][5] = -2  # Entrance
    grid[0][25] = -1  # Exit

    r_start = 3  # Start row for shelves
    c_start = 1  # Start col for shelves

    # Flatten aisles by category order
    aisles_flat = []
    for cat in category_order:
        aisles_flat.extend([int(aisle_id) for aisle_id, _ in categorized[cat]])

    # Place aisles in the grid, grouped by category
    idx = 0
    for c in range(c_start, cols - 1, 5):
        for r in range(r_start, rows - 1, 3):
            if idx >= len(aisles_flat):
                break
            aisle_id = aisles_flat[idx]
            grid[r][c] = aisle_id
            grid[r][c + 1] = aisle_id
            grid[r][c + 2] = aisle_id
            idx += 1
            # Place on opposite side if more aisles
            if idx < len(aisles_flat):
                aisle_id = aisles_flat[idx]
                grid[r + 1][c] = aisle_id
                grid[r + 1][c + 1] = aisle_id
                grid[r + 1][c + 2] = aisle_id
                idx += 1

    grid_input = GridInput(rows=rows, cols=cols, grid=grid.tolist(), entrance=(0, 5), exit=(0, 25))
    super_grid = SupermarketGrid.from_dict(grid_input, aisle_info_file=cfg.AISLE_INFO_FILE)
    return super_grid


def gen_block_category_layout() -> SupermarketGrid:
    """
    Generate a supermarket layout with clear blocks separating categories.
    Each category is placed in a horizontal band, separated by empty rows.
    """
    categorized = separate_by_category()
    category_order = [
        "food",
        "beverages",
        "special diet",
        "condiments",
        "household",
        "personal care",
        "pet",
        "baby",
        "other",
    ]

    rows = 36
    cols = 35
    grid = np.zeros((rows, cols), dtype=int)
    grid[0][5] = -2  # Entrance
    grid[0][25] = -1  # Exit

    band_height = 3  # Height of each category block (in shelf rows)
    gap = 2  # Empty rows between blocks
    c_start = 1  # Start col for shelves

    current_row = 3  # Start after entrance rows

    for cat in category_order:
        aisles = [int(aisle_id) for aisle_id, _ in categorized[cat]]
        idx = 0
        # Fill the block for this category
        for r in range(current_row, min(current_row + band_height, rows - 1)):
            for c in range(c_start, cols - 1, 5):
                if idx >= len(aisles):
                    break
                aisle_id = aisles[idx]
                grid[r][c] = aisle_id
                grid[r][c + 1] = aisle_id
                grid[r][c + 2] = aisle_id
                idx += 1
                # Place on opposite side if more aisles
                if idx < len(aisles):
                    aisle_id = aisles[idx]
                    grid[r + 1][c] = aisle_id
                    grid[r + 1][c + 1] = aisle_id
                    grid[r + 1][c + 2] = aisle_id
                    idx += 1
            if idx >= len(aisles):
                break
        current_row += band_height + gap  # Move to next block, leaving a gap

        if current_row >= rows - 1:
            break  # No more space

    grid_input = GridInput(rows=rows, cols=cols, grid=grid.tolist(), entrance=(0, 5), exit=(0, 25))
    super_grid = SupermarketGrid.from_dict(grid_input, aisle_info_file=cfg.AISLE_INFO_FILE)
    return super_grid


def gen_island_category_layout() -> SupermarketGrid:
    """
    Generate a supermarket layout with distinct 'island' zones for each category.
    Each category is placed in its own block, separated by empty space and walkable paths.
    All aisles are placed, and all are accessible.
    """
    categorized = separate_by_category()
    # Only use categories with aisles
    categories = [cat for cat in categorized if len(categorized[cat]) > 0]

    shelf_width = 3  # Each aisle takes 3 columns
    path_width = 1  # Path between shelves
    zone_gap = 3  # Gap between zones

    # Calculate per-category zone dimensions for squareness
    zone_dims = []
    for cat in categories:
        n = len(categorized[cat])
        aisles_per_row = max(1, math.ceil(math.sqrt(n)))
        needed_rows = math.ceil(n / aisles_per_row)
        zone_width = aisles_per_row * (shelf_width + path_width)
        zone_height = needed_rows * (1 + path_width)
        zone_dims.append((zone_width, zone_height, aisles_per_row, needed_rows))

    # Arrange zones in a grid as square as possible
    num_zones = len(categories)
    zone_cols = math.ceil(math.sqrt(num_zones))
    zone_rows = math.ceil(num_zones / zone_cols)
    max_zone_width = max(z[0] for z in zone_dims)
    max_zone_height = max(z[1] for z in zone_dims)

    # Calculate total grid size
    rows = zone_rows * max_zone_height + (zone_rows + 1) * zone_gap + 3  # +3 for entrance/exit
    cols = zone_cols * max_zone_width + (zone_cols + 1) * zone_gap

    grid = np.zeros((rows, cols), dtype=int)
    grid[0][5] = -2  # Entrance
    grid[0][cols - 6] = -1  # Exit

    # Place each category in its own zone
    for idx, cat in enumerate(categories):
        aisles = [int(aisle_id) for aisle_id, _ in categorized[cat]]
        zone_w, zone_h, aisles_per_row, needed_rows = zone_dims[idx]
        zone_r = idx // zone_cols
        zone_c = idx % zone_cols
        r0 = 3 + zone_gap + zone_r * (max_zone_height + zone_gap)
        c0 = zone_gap + zone_c * (max_zone_width + zone_gap)
        ai = 0
        for row in range(needed_rows):
            r = r0 + row * (1 + path_width)
            for col in range(aisles_per_row):
                c = c0 + col * (shelf_width + path_width)
                if ai >= len(aisles):
                    break
                grid[r][c] = aisles[ai]
                grid[r][c + 1] = aisles[ai]
                grid[r][c + 2] = aisles[ai]
                ai += 1
            if ai >= len(aisles):
                break

    grid_input = GridInput(rows=rows, cols=cols, grid=grid.tolist(), entrance=(0, 5), exit=(0, cols - 6))
    super_grid = SupermarketGrid.from_dict(grid_input, aisle_info_file=cfg.AISLE_INFO_FILE)
    return super_grid


def separate_by_category():
    with open(cfg.AISLE_INFO_FILE, "r") as file:
        aisles_data = json.load(file)

    # Define subcategories and keywords
    categories = {
        "bakery": [
            "bakery",
            "bread",
            "buns",
            "rolls",
            "cakes",
            "cookies",
            "desserts",
            "doughs",
            "pudding",
            "gelatins",
            "bake mixes",
        ],
        "dairy": ["milk", "cheese", "yogurt", "cream", "butter"],
        "produce": ["fruits", "vegetables", "herbs", "produce", "applesauce", "dried fruit"],
        "meat & seafood": [
            "meat",
            "poultry",
            "seafood",
            "bacon",
            "sausage",
            "hot dogs",
            "packaged meat",
            "packaged seafood",
        ],
        "frozen": ["frozen", "ice cream", "appetizers", "sides", "prepared meals", "prepared soups", "instant foods"],
        "snacks": [
            "snacks",
            "chips",
            "pretzels",
            "crackers",
            "popcorn",
            "jerky",
            "granola",
            "bars",
            "candy",
            "chocolate",
            "nuts",
            "seeds",
            "trail mix",
            "snack mix",
            "gum",
        ],
        "breakfast": ["breakfast", "cereal", "granola", "pancake", "waffle", "oatmeal"],
        "condiments & sauces": [
            "sauces",
            "condiments",
            "spices",
            "seasonings",
            "marinades",
            "meat preparation",
            "pasta sauce",
            "honeys",
            "syrups",
            "nectars",
            "oils",
            "vinegars",
            "dips",
            "spreads",
            "pickled",
            "olives",
        ],
        "international": ["latino", "asian", "indian", "kosher", "specialty", "tofu", "alternative"],
        "beverages - nonalcoholic": [
            "drink",
            "juice",
            "water",
            "seltzer",
            "sparkling",
            "tea",
            "coffee",
            "cocoa",
            "soft drinks",
        ],
        "beverages - alcoholic": ["wine", "beer", "cooler", "red wines", "spirits"],
        "household": [
            "cleaning",
            "trash",
            "paper",
            "storage",
            "laundry",
            "dish",
            "air freshener",
            "candles",
            "plates",
            "bowls",
            "cups",
            "flatware",
            "kitchen supplies",
            "more household",
            "soap",
        ],
        "personal care": [
            "oral",
            "hygiene",
            "shave",
            "deodorant",
            "skin",
            "hair",
            "facial",
            "body",
            "bath",
            "beauty",
            "feminine",
            "vitamins",
            "supplements",
            "first aid",
            "cold flu",
            "allergy",
            "eye",
            "ear",
            "digestion",
            "pain relief",
            "muscles",
            "joints",
        ],
        "pet": ["dog", "cat", "pet"],
        "baby": ["baby", "diapers", "wipes"],
        "special diet": ["soy", "lactosefree", "protein meal replacements", "special diet"],
        # fallback for anything not matched
        "misc food": [],
        "misc nonfood": [],
    }

    categorized = {cat: [] for cat in categories}

    for aisle_id, data in aisles_data.items():
        aisle_name = data["aisle_name"].lower()
        found = False
        for cat, keywords in categories.items():
            if any(keyword in aisle_name for keyword in keywords):
                categorized[cat].append((aisle_id, aisle_name))
                found = True
                break
        if not found:
            # Assign "other" to misc food if it looks like food, else misc nonfood
            if any(
                word in aisle_name
                for word in [
                    "food",
                    "meal",
                    "soup",
                    "pasta",
                    "produce",
                    "fruit",
                    "vegetable",
                    "meat",
                    "cheese",
                    "bakery",
                    "snack",
                    "sauce",
                    "spice",
                    "seasoning",
                    "dairy",
                    "egg",
                    "seafood",
                ]
            ):
                categorized["misc food"].append((aisle_id, aisle_name))
            else:
                categorized["misc nonfood"].append((aisle_id, aisle_name))

    # Print summary
    for cat, aisles in categorized.items():
        print(f"\nCategory: {cat} ({len(aisles)} aisles)")
        for aisle_id, aisle_name in aisles:
            print(f"  {aisle_id}: {aisle_name}")

    print("-" * 40)
    print("Total aisles:", len(aisles_data))
    print("Total new aisles:", sum(len(aisles) for aisles in categorized.values()))
    return categorized


if __name__ == "__main__":
    pass
