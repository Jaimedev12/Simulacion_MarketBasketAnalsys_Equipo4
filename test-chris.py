import utils.gen_multiple_layouts as gen_multiple_layouts
import visualization.visualization as vis

if __name__ == "__main__":
    print(gen_multiple_layouts.separate_by_category())

    vis.plot_grid_with_ids(gen_multiple_layouts.gen_serpentine_layout())
