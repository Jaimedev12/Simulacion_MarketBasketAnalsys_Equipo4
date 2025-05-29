import utils.gen_multiple_layouts as gen_multiple_layouts
import visualization.visualization as vis

if __name__ == "__main__":
    layout = gen_multiple_layouts.gen_serpentine_layout()

    vis.plot_grid_with_ids(layout)
    # print(layout.grid)
