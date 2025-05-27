import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import numpy as np
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from optimization.tabu_search import Iteration
import matplotlib.widgets as widgets
import config as cfg

class ResultVisualizer:
    def __init__(self, iterations: List[Iteration]):
        self.iterations: List[Iteration] = iterations
        self.current_iteration = 0
        self.grid_matrices = []
        self.aisle_info = self._load_aisle_info()
        self._prepare_grid_data()
        
    def _load_aisle_info(self) -> Dict[str, Dict[str, Any]]:
        """Load aisle information from the JSON file"""
        try:
            with open(cfg.AISLE_INFO_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load aisle info: {e}")
            return {}
    
    def _prepare_grid_data(self):
        """Convert iteration data to grid matrices for visualization"""
        if not self.iterations:
            return
            
        for iteration in self.iterations:
            grid = iteration.grid
            rows, cols = grid.rows, grid.cols
            matrix = np.zeros((rows, cols), dtype=int)
            
            for i in range(rows):
                for j in range(cols):
                    matrix[i, j] = grid.grid[i][j].aisle_id
                    
            self.grid_matrices.append(matrix)
    
    def visualize(self):
        """Display the grid with a slider for iteration navigation"""
        if not self.iterations or not self.grid_matrices:
            print("No iterations to visualize.")
            return
            
        # Set up the figure and axes
        fig, ax = plt.subplots(figsize=(12, 10))
        plt.subplots_adjust(bottom=0.2)  # Make room for the slider
        
        # Get unique aisle IDs for color mapping
        all_aisle_ids = np.unique(np.concatenate([m.flatten() for m in self.grid_matrices]))
        max_aisle_id = max(all_aisle_ids)
        
        # Create custom colors for visualization
        custom_colors = {
            0: "white",    # Walkable space
            -1: "red",     # Exit
            -2: "green",   # Entrance
        }
        
        # Generate colors for aisle IDs
        for i in range(1, max_aisle_id + 1):
            color_tuple = plt.get_cmap('tab20')(i % 20)
            custom_colors[i] = mcolors.to_hex(color_tuple)
            
        # Create a colormap - add "highlighted" version at the end
        base_colors = [custom_colors.get(i, "gray") for i in range(max_aisle_id + 1)]
        highlight_colors = ["#FFA500", "#CCCCCC"]  # Orange for highlighting
        color_list = base_colors + highlight_colors
        cmap = ListedColormap(color_list)
        
        # Store original data and create a copy for modifications
        current_grid_idx = 0
        grid_data = self.grid_matrices[current_grid_idx].copy()
        highlighted_grid = grid_data.copy()
        
        # Initial plot
        im = ax.imshow(highlighted_grid, cmap=cmap, interpolation="nearest", vmin=-2, vmax=max_aisle_id + 2)
        ax.set_title(f"Layout - Iteration {self.current_iteration}")
        
        # Add text labels - we'll keep these static to improve performance
        text_labels = []
        for i in range(grid_data.shape[0]):
            for j in range(grid_data.shape[1]):
                cell_value = grid_data[i, j]
                if cell_value != 0:  # Only label non-walkable cells
                    text = ax.text(j, i, str(cell_value), ha="center", va="center", 
                            color="black", fontsize=8)
                    text_labels.append(text)
        
        # Create info box for aisle data
        info_text = ax.text(0.02, 0.02, "", transform=ax.transAxes, fontsize=10,
                           bbox=dict(facecolor='white', alpha=0.8))
        
        # Add a slider for iteration selection
        ax_slider = plt.axes((0.25, 0.1, 0.65, 0.03))
        slider = widgets.Slider(
            ax=ax_slider,
            label='Iteration',
            valmin=0,
            valmax=len(self.iterations) - 1,
            valinit=0,
            valstep=1
        )
        
        # Last hovered aisle for efficient updates
        last_hovered_aisle = None
        
        # Update function for slider
        def update(val):
            nonlocal current_grid_idx, grid_data, highlighted_grid, last_hovered_aisle
            
            # Reset hover tracking
            last_hovered_aisle = None
            
            # Update the current iteration index
            current_grid_idx = int(slider.val)
            
            # Update the base data
            grid_data = self.grid_matrices[current_grid_idx].copy()
            highlighted_grid = grid_data.copy()
            
            # Update the image data directly - much faster than clearing and redrawing
            im.set_array(highlighted_grid)
            
            # Clear info text
            info_text.set_text("")
            
            # Update title
            ax.set_title(f"Layout - Iteration {current_grid_idx}")
            
            # Update text labels - could be optimized further
            for text in text_labels:
                text.remove()
            text_labels.clear()
            
            for i in range(grid_data.shape[0]):
                for j in range(grid_data.shape[1]):
                    cell_value = grid_data[i, j]
                    if cell_value != 0:  # Only label non-walkable cells
                        text = ax.text(j, i, str(cell_value), ha="center", va="center", 
                                color="black", fontsize=8)
                        text_labels.append(text)
            
            fig.canvas.draw_idle()
        
        slider.on_changed(update)
        
        # Add a highlight feature on mouse hover
        def hover(event):
            nonlocal highlighted_grid, last_hovered_aisle, grid_data
            
            if event.inaxes == ax:
                x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
                if (0 <= y < grid_data.shape[0] and 0 <= x < grid_data.shape[1]):
                    aisle_id = grid_data[y, x]
                    
                    # Only do work if we're hovering over a different aisle than before
                    if aisle_id != last_hovered_aisle:
                        # Update title
                        ax.set_title(f"Layout - Iteration {current_grid_idx} - Aisle {aisle_id}")
                        
                        # Reset highlighted grid to original data
                        highlighted_grid = grid_data.copy()
                        
                        # Update info text with aisle data if available
                        if aisle_id > 0 and str(aisle_id) in self.aisle_info:
                            aisle_data = self.aisle_info[str(aisle_id)]
                            aisle_name = aisle_data.get('aisle_name', 'Unknown')
                            impulse_idx = aisle_data.get('impulse_index', 0)
                            product_count = aisle_data.get('product_count', 0)
                            
                            info_str = (f"Aisle: {aisle_id} - {aisle_name}\n"
                                       f"Impulse Index: {impulse_idx:.3f}\n"
                                       f"Product Count: {product_count}")
                            
                            info_text.set_text(info_str)
                        else:
                            if aisle_id == 0:
                                info_text.set_text("Walkway")
                            elif aisle_id == -1:
                                info_text.set_text("Exit")
                            elif aisle_id == -2:
                                info_text.set_text("Entrance")  
                            else:
                                info_text.set_text(f"Aisle: {aisle_id} (No data available)")
                        
                        # Highlight cells with the same aisle ID
                        if aisle_id > 0:  # Only highlight actual aisles, not walkable/entry/exit
                            # First check if we have any matching cells
                            matching_mask = (grid_data == aisle_id)
                            matching_count = np.sum(matching_mask)

                            # Gray out all non-walkable cells first
                            non_walkable_mask = (grid_data > 0)
                            highlighted_grid[non_walkable_mask] = max_aisle_id + 1  # Gray color

                            # Then highlight matching cells in orange
                            highlighted_grid[matching_mask] = max_aisle_id + 0  # Orange color
                        
                        # Update the image data directly - much faster than clearing and redrawing
                        im.set_array(highlighted_grid)
                        
                        # Remember which aisle we're hovering over
                        last_hovered_aisle = aisle_id
                        
                        # Trigger a redraw of just the modified parts
                        fig.canvas.draw_idle()
        
        def on_leave(event):
            nonlocal highlighted_grid, last_hovered_aisle, grid_data
            
            if last_hovered_aisle is not None:
                # Reset the grid to original state
                highlighted_grid = grid_data.copy()
                im.set_array(highlighted_grid)
                ax.set_title(f"Layout - Iteration {current_grid_idx}")
                info_text.set_text("")
                last_hovered_aisle = None
                fig.canvas.draw_idle()
        
        fig.canvas.mpl_connect("motion_notify_event", hover)
        fig.canvas.mpl_connect("axes_leave_event", on_leave)
        
        plt.show()