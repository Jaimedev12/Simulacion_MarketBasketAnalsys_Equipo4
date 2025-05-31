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


def gen_serpentine_layout() -> SupermarketGrid:
    """
    Generate a supermarket layout with a serpentine/maze pattern:
    - First two rows: paths (all zeros)
    - Next two rows: aisles flush left (space at right)
    - Next two rows: paths
    - Next two rows: aisles flush right (space at left)
    - Repeat as needed
    The number of columns is a multiple of 3 + 1 (aisle width + path).
    """
    categorized = separate_by_category()
    all_aisles = []
    for cat in categorized:
        all_aisles.extend([int(aisle_id) for aisle_id, _ in categorized[cat]])
    total_aisles = len(all_aisles)

    shelf_width = 3
    max_aisles_per_row = 10
    aisles_per_row = min(max_aisles_per_row, (total_aisles + 1) // 2)
    n_cols = aisles_per_row * shelf_width + 1  # +1 for the path

    # Estimate number of aisle rows needed
    aisle_rows_needed = (total_aisles + aisles_per_row - 1) // aisles_per_row
    # Each block is 2 path rows + 2 aisle rows
    block_rows = 4
    n_blocks = (aisle_rows_needed + 1) // 2
    n_rows = n_blocks * block_rows + 2

    grid = np.zeros((n_rows, n_cols), dtype=int)
    entrance_col = n_cols // 2
    grid[0][entrance_col] = -2  # Entrance
    grid[n_rows - 1][entrance_col] = -1  # Exit

    ai = 0
    row = 0
    aisle_row_counter = 0
    while ai < total_aisles and row < n_rows:
        # Skip path rows
        if row % 4 < 2:
            row += 1
            continue
        # Alternate block every two aisle rows
        block = (aisle_row_counter // 2) % 2  # 0: left aisles, 1: right aisles
        if block == 0:
            # Aisles flush left, space at right
            c = 0
            while c + shelf_width <= n_cols - 1 and ai < total_aisles:
                for w in range(shelf_width):
                    grid[row][c + w] = all_aisles[ai]
                ai += 1
                c += shelf_width
            # Path at far right
            grid[row][n_cols - 1] = 0
        else:
            print(f"Placing aisles in row {row} (block {block})")
            # Aisles flush right, space at left
            grid[row][0] = 0
            c = 1
            while c + shelf_width <= n_cols and ai < total_aisles:
                for w in range(shelf_width):
                    grid[row][c + w] = all_aisles[ai]
                ai += 1
                c += shelf_width
        row += 1
        aisle_row_counter += 1

    grid_input = GridInput(
        rows=n_rows,
        cols=n_cols,
        grid=grid.tolist(),
        entrance=(0, entrance_col),
        exit=(n_rows - 1, entrance_col),
    )
    super_grid = SupermarketGrid.from_dict(grid_input, aisle_info_file=cfg.AISLE_INFO_FILE)
    return super_grid


def get_categories_by_impulse(categorized, aisles_data):
    """
    Returns a list of categories sorted by total impulse_index (descending).
    """
    cat_impulse = {}
    for cat in categorized:
        total_impulse = sum(
            aisles_data[aid]["impulse_index"] for aid, _ in categorized[cat] if "impulse_index" in aisles_data[aid]
        )
        cat_impulse[cat] = total_impulse
    sorted_cats = sorted(
        [cat for cat in categorized if len(categorized[cat]) > 0], key=lambda c: cat_impulse[c], reverse=True
    )
    return sorted_cats, cat_impulse


def gen_category_rings_layout() -> SupermarketGrid:
    """
    Place aisles in concentric rings around a central plaza,
    with the most impulsive categories closer to the center.
    Rings are filled from inside out, continuing categories as needed.
    """
    # Load aisle data with impulse_index
    with open(cfg.AISLE_INFO_FILE, "r") as file:
        aisles_data = json.load(file)

    categorized = separate_by_category()
    sorted_cats, cat_impulse = get_categories_by_impulse(categorized, aisles_data)

    shelf_width = 5
    path_width = 1
    ring_gap = 1
    # 6 12
    initial_side = 10  # Minimum side length for the innermost ring

    # Flatten all aisles, sorted by impulse category order
    all_aisles = []
    for cat in sorted_cats:
        all_aisles.extend([int(aid) for aid, _ in categorized[cat]])
    total_aisles = len(all_aisles)

    # Estimate max grid size needed
    max_rings = 1
    aisles_left = total_aisles
    side = initial_side
    while aisles_left > 0:
        ring_perimeter = 4 * side
        aisles_in_ring = ring_perimeter // (shelf_width + path_width)
        aisles_left -= aisles_in_ring
        side += 2 * (shelf_width + path_width + ring_gap)
        max_rings += 1
    grid_size = side + 10
    rows = cols = grid_size
    grid = np.zeros((rows, cols), dtype=int)
    center = (rows // 2, cols // 2)

    # Place entrance and exit at top and bottom center
    grid[0][cols // 2] = -2
    grid[rows - 1][cols // 2] = -1

    ai = 0
    ring_idx = 0
    side = initial_side
    while ai < total_aisles:
        ring_perimeter = 4 * side
        aisles_in_ring = ring_perimeter // (shelf_width + path_width)
        ring_radius = side // 2 + ring_gap * ring_idx
        top = center[0] - ring_radius
        bottom = center[0] + ring_radius
        left = center[1] - ring_radius
        right = center[1] + ring_radius

        # Defensive bounds check
        if top < 0 or left < 0 or bottom >= rows or right >= cols:
            break

        placed = 0

        # Top edge (left to right)
        c = left
        while c + shelf_width - 1 <= right and ai < total_aisles:
            if all(grid[top][c + w] == 0 for w in range(shelf_width)):
                for w in range(shelf_width):
                    grid[top][c + w] = all_aisles[ai]
                ai += 1
                placed += 1
                c += shelf_width + path_width
            else:
                c += 1  # Only move by 1 if can't place

        # Right edge (top to bottom)
        r = top + 1
        while r + shelf_width - 1 <= bottom and ai < total_aisles:
            if all(grid[r + w][right] == 0 for w in range(shelf_width)):
                for w in range(shelf_width):
                    grid[r + w][right] = all_aisles[ai]
                ai += 1
                placed += 1
                r += shelf_width + path_width
            else:
                r += 1

        # Bottom edge (right to left)
        c = right - 1
        while c - shelf_width + 1 >= left and ai < total_aisles:
            if all(grid[bottom][c - w] == 0 for w in range(shelf_width)):
                for w in range(shelf_width):
                    grid[bottom][c - w] = all_aisles[ai]
                ai += 1
                placed += 1
                c -= shelf_width + path_width
            else:
                c -= 1

        # Left edge (bottom to top)
        r = bottom - 1
        while r - shelf_width + 1 > top and ai < total_aisles:
            if all(grid[r - w][left] == 0 for w in range(shelf_width)):
                for w in range(shelf_width):
                    grid[r - w][left] = all_aisles[ai]
                ai += 1
                placed += 1
                r -= shelf_width + path_width
            else:
                r -= 1

        ring_idx += 1
        side += 2 * (shelf_width + path_width + ring_gap)

    grid_input = GridInput(
        rows=rows,
        cols=cols,
        grid=grid.tolist(),
        entrance=(0, cols // 2),
        exit=(rows - 1, cols // 2),
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

    return categorized


def get_all_layouts():
    """
    Generate all predefined layouts.
    """
    island_layout = gen_island_category_layout()
    central_plaza_layout = gen_central_plaza_layout()
    serpentine_layout = gen_serpentine_layout()
    category_rings_layout = gen_category_rings_layout()

    # Clear console
    print("\033c", end="")

    return [
        {"name": "island_category", "layout": island_layout},
        # {"name": "central_plaza", "layout": central_plaza_layout},
        # {"name": "serpentine", "layout": serpentine_layout},
        {"name": "category_rings", "layout": category_rings_layout},
    ]


if __name__ == "__main__":
    pass
