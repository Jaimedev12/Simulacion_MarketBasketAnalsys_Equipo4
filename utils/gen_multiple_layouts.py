import json
import numpy as np
from core.grid import SupermarketGrid, GridInput
import config as cfg
import math
import random


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


def gen_central_plaza_layout() -> SupermarketGrid:
    """
    Generate a supermarket layout with a central plaza and categories as spokes radiating out.
    All aisles are accessible from the entrance, through the plaza, to the exit.
    Dynamically increases grid size if not all aisles can be placed.
    """
    categorized = separate_by_category()
    categories = [cat for cat in categorized if len(categorized[cat]) > 0]
    num_spokes = len(categories)

    # Layout parameters
    shelf_width = 3
    path_width = 1
    spoke_gap = 4
    max_aisles_per_spoke = max(len(categorized[cat]) for cat in categories)
    aisles_per_row = math.ceil(math.sqrt(max_aisles_per_spoke)) + 2  # Add extra space

    # Try increasing plaza/grid size until all aisles are placed or max attempts reached
    max_attempts = 5
    for attempt in range(max_attempts):
        plaza_size = 11 + attempt * 4  # Increase plaza size each attempt
        rows = plaza_size + 2 * (aisles_per_row * (1 + path_width) + spoke_gap)
        cols = plaza_size + 2 * (aisles_per_row * (shelf_width + path_width) + spoke_gap)
        grid = np.zeros((rows, cols), dtype=int)

        # Plaza coordinates
        plaza_r0 = (rows - plaza_size) // 2
        plaza_c0 = (cols - plaza_size) // 2

        # Place entrance and exit at opposite sides of the plaza
        grid[plaza_r0][plaza_c0 + plaza_size // 2] = -2  # Entrance (top center of plaza)
        grid[plaza_r0 + plaza_size - 1][plaza_c0 + plaza_size // 2] = -1  # Exit (bottom center of plaza)

        angle_step = 2 * math.pi / num_spokes
        placed_summary = {}
        total_placed = 0

        random.shuffle(categories)

        for idx, cat in enumerate(categories):
            aisles = [int(aisle_id) for aisle_id, _ in categorized[cat]]
            angle = idx * angle_step
            center_r = plaza_r0 + plaza_size // 2
            center_c = plaza_c0 + plaza_size // 2
            dr = round(math.sin(angle))
            dc = round(math.cos(angle))
            r = center_r + dr * (plaza_size // 2 + 1)
            c = center_c + dc * (plaza_size // 2 + 1)
            ai = 0
            for row in range(aisles_per_row):
                rr = r + dr * row * (1 + path_width)
                cc = c + dc * row * (shelf_width + path_width)
                for col in range(aisles_per_row):
                    if abs(dr) > abs(dc):  # Vertical spoke
                        rrr = rr
                        ccc = cc + (col - aisles_per_row // 2) * (shelf_width + path_width)
                    else:  # Horizontal spoke
                        rrr = rr + (col - aisles_per_row // 2) * (1 + path_width)
                        ccc = cc

                    # Check bounds for full shelf
                    if 0 <= rrr < rows - 1 and 0 <= ccc <= cols - 3 and ai < len(aisles):
                        # Check if all three cells are empty
                        if grid[rrr][ccc] == 0 and grid[rrr][ccc + 1] == 0 and grid[rrr][ccc + 2] == 0:
                            grid[rrr][ccc] = aisles[ai]
                            grid[rrr][ccc + 1] = aisles[ai]
                            grid[rrr][ccc + 2] = aisles[ai]
                            print(f"Placed aisle {aisles[ai]} for category '{cat}' at ({rrr},{ccc})-({rrr},{ccc + 2})")
                            ai += 1
                        else:
                            print(
                                f"WARNING: Overlap detected, could not place aisle {aisles[ai]} for category '{cat}' at ({rrr},{ccc})"
                            )
                    elif ai < len(aisles):
                        print(
                            f"WARNING: Could not place full shelf for aisle {aisles[ai]} of category '{cat}' at ({rrr},{ccc})"
                        )
                    if ai >= len(aisles):
                        break
                if ai >= len(aisles):
                    break
            placed_summary[cat] = ai
            total_placed += ai

        # Print summary of placement
        print(f"\nCentral Plaza Layout Placement Summary (attempt {attempt + 1}):")
        for cat in categories:
            print(f"  {cat}: {placed_summary[cat]} aisles placed (of {len(categorized[cat])})")
        print(f"Total aisles placed: {total_placed} (of {sum(len(categorized[cat]) for cat in categories)})\n")

        # If all aisles placed, break
        if total_placed == sum(len(categorized[cat]) for cat in categories):
            break
        else:
            print("Not all aisles placed, increasing grid/plaza size and retrying...\n")

    grid_input = GridInput(
        rows=rows,
        cols=cols,
        grid=grid.tolist(),
        entrance=(plaza_r0, plaza_c0 + plaza_size // 2),
        exit=(plaza_r0 + plaza_size - 1, plaza_c0 + plaza_size // 2),
    )
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
