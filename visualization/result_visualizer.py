from matplotlib import colors
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
            
        # Set up the figure and axes with a side panel for information
        fig = plt.figure(figsize=(16, 9))
            
        # Create a layout with grid on left and info panel on right
        cbar_ax = fig.add_subplot(1, 32, 6)  # Grid takes 1/32 of width
        grid_ax = fig.add_subplot(1, 4, (2, 3))  # Grid takes 2/4 of width
        info_ax = fig.add_subplot(1, 4, 4)       # Info panel takes 1/4 of width
        
        # Create radio buttons on the side panel - make it taller to accommodate 4 options
        ax_radio = plt.axes((0.07, 0.1, 0.15, 0.2))
        
        # Hide axes for info panel but keep border
        info_ax.set_xticks([])
        info_ax.set_yticks([])
        
        # Set up info panel title
        info_ax.set_title("Aisle Information")
        
        # Add an empty text box in the info panel
        info_text = info_ax.text(0.05, 0.6, "", 
                            verticalalignment='top', 
                            wrap=True,
                            fontsize=11)
        
        score_text = info_ax.text(0.05, 0.95, "", 
                        verticalalignment='top',
                        wrap=True,
                        fontsize=11,
                        fontweight='bold',
                        color='navy')
        
        plt.subplots_adjust(bottom=0.10)

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
        cmap_layout = ListedColormap(color_list)

        # Use different colormaps for different heatmap types
        cmap_impulse_index = plt.cm.get_cmap('viridis')    # For impulse index (potential)
        cmap_purchases = plt.cm.get_cmap('plasma')         # For actual purchases
        cmap_walking = plt.cm.get_cmap('hot')             # For walking paths (hot colormap)
        
        # Store original data and create a copy for modifications
        current_grid_idx = 0
        grid_data = self.grid_matrices[current_grid_idx].copy()
        highlighted_grid = grid_data.copy()
        
        # Track current visualization mode
        vis_mode = 'layout'  # 'layout', 'heatmap', 'purchases' or 'walking'
        
        # Create function to generate impulse index grid
        def create_impulse_grid(grid):
            impulse_grid = np.zeros_like(grid, dtype=float)
            
            # First pass: collect all valid impulse index values to find min/max
            all_impulse_values = []
            for aisle_id_str, aisle_data in self.aisle_info.items():
                if 'impulse_index' in aisle_data:
                    all_impulse_values.append(aisle_data['impulse_index'])
            
            # If we have values, calculate min and max for normalization
            if all_impulse_values:
                min_impulse = min(all_impulse_values)
                max_impulse = max(all_impulse_values)
                impulse_range = max_impulse - min_impulse
            else:
                # Default values if no impulse data found
                min_impulse = 0
                impulse_range = 1  # Avoid division by zero
            
            # Second pass: build the grid with normalized values
            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    aisle_id = grid[i, j]
                    if aisle_id > 0 and str(aisle_id) in self.aisle_info:
                        raw_value = self.aisle_info[str(aisle_id)].get('impulse_index', 0)
                        # Normalize to 0-1 range
                        if impulse_range > 0:
                            impulse_grid[i, j] = (raw_value - min_impulse) / impulse_range
                        else:
                            impulse_grid[i, j] = 0
                    else:
                        # Keep special values for entrance/exit
                        if aisle_id < 0:
                            impulse_grid[i, j] = -1  # We'll handle these specially
                        else:
                            impulse_grid[i, j] = 0
                            
            return impulse_grid
        
        # Initial impulse grid
        impulse_grid = create_impulse_grid(grid_data)
        
        # Get the purchase heatmap from the iteration data
        purchase_heatmap = self.iterations[current_grid_idx].impulse_heat_map
        
        # Get the walking heatmap from the iteration data
        walking_heatmap = self.iterations[current_grid_idx].walk_heat_map

        # Initial plot
        im = grid_ax.imshow(highlighted_grid, cmap=cmap_layout, interpolation="nearest", vmin=-2, vmax=max_aisle_id + 2)
        grid_ax.set_title(f"Layout - Iteration {self.current_iteration}")
        
        # Add text labels - make them smaller to reduce overlap
        text_labels = []
        def update_text_labels():
            nonlocal text_labels
            # Clear existing labels
            for text in text_labels:
                text.remove()
            text_labels.clear()
            
            # Only add labels in layout mode
            if vis_mode == 'layout':
                for i in range(grid_data.shape[0]):
                    for j in range(grid_data.shape[1]):
                        cell_value = grid_data[i, j]
                        if cell_value != 0:  # Only label non-walkable cells
                            text = grid_ax.text(j, i, str(cell_value), ha="center", va="center", 
                                    color="black", fontsize=7)
                            text_labels.append(text)
        
        update_text_labels()
        
        # Function to update score information
        def update_score_info(idx):
            iteration = self.iterations[idx]
            score_info = (f"Score Information:\n\n"
                        f"Total Score: {iteration.score.total_score:.2f}\n\n"
                        f"Adjusted Purchases: {iteration.score.adjusted_purchases:.2f}\n\n"
                        f"Adjusted Steps: {iteration.score.adjusted_steps:.2f}")
            score_text.set_text(score_info)
        
        # Update initial score info
        update_score_info(current_grid_idx)

        # AFTER tight_layout(), create the slider axes at the bottom
        ax_slider = plt.axes((0.2, 0.05, 0.6, 0.03))
        slider = widgets.Slider(
            ax=ax_slider,
            label='Iteration',
            valmin=0,
            valmax=len(self.iterations) - 1,
            valinit=0,
            valstep=1
        )
        
        # Add a fourth option for walking heatmap
        radio = widgets.RadioButtons(
            ax_radio, 
            ('Layout', 'Impulse Index', 'Purchase Heatmap', 'Walking Heatmap'), 
            active=0
        )
        ax_radio.set_title("Display Mode")

        # Last hovered aisle for efficient updates
        last_hovered_aisle = None
        
        cbar = plt.colorbar(plt.cm.ScalarMappable(norm=colors.Normalize(0.0, 1.0), cmap=cmap_impulse_index), 
                        cax=cbar_ax)
        cbar.set_label('Impulse Index')
        cbar_ax.set_visible(False)
        
        # Update function for slider
        def update(val):
            nonlocal current_grid_idx, grid_data, highlighted_grid, last_hovered_aisle, impulse_grid, purchase_heatmap, walking_heatmap
            
            # Reset hover tracking
            last_hovered_aisle = None
            
            # Update the current iteration index
            current_grid_idx = int(slider.val)
            
            # Update the base data
            grid_data = self.grid_matrices[current_grid_idx].copy()
            highlighted_grid = grid_data.copy()
            impulse_grid = create_impulse_grid(grid_data)
            purchase_heatmap = self.iterations[current_grid_idx].impulse_heat_map
            walking_heatmap = self.iterations[current_grid_idx].walk_heat_map
            
            # Update visualization based on current mode
            if vis_mode == 'layout':
                im.set_array(highlighted_grid)
                im.set_cmap(cmap_layout)
                im.set_clim(vmin=-2, vmax=max_aisle_id + 2)
                cbar_ax.set_visible(False)
            elif vis_mode == 'heatmap':
                im.set_array(impulse_grid)
                im.set_cmap(cmap_impulse_index)
                im.set_clim(vmin=0, vmax=1)  # Impulse index ranges from 0 to 1
                cbar.set_label('Impulse Index')
                cbar.mappable.set_cmap(cmap_impulse_index)
                cbar_ax.set_visible(True)
            elif vis_mode == 'purchases':
                im.set_array(purchase_heatmap)
                im.set_cmap(cmap_purchases)
                im.set_clim(vmin=0, vmax=1)  # Normalized purchase heatmap
                cbar.set_label('Purchase Frequency')
                cbar.mappable.set_cmap(cmap_purchases)
                cbar_ax.set_visible(True)
            else:  # walking mode
                im.set_array(walking_heatmap)
                im.set_cmap(cmap_walking)
                im.set_clim(vmin=0, vmax=1)  # Normalized walking heatmap
                cbar.set_label('Walking Frequency')
                cbar.mappable.set_cmap(cmap_walking)
                cbar_ax.set_visible(True)
            
            # Clear aisle info text
            info_text.set_text("")
            
            # Update score information
            update_score_info(current_grid_idx)
            
            # Update title based on mode
            if vis_mode == 'layout':
                grid_ax.set_title(f"Layout - Iteration {current_grid_idx}")
            elif vis_mode == 'heatmap':
                grid_ax.set_title(f"Impulse Index Heatmap - Iteration {current_grid_idx}")
            elif vis_mode == 'purchases':
                grid_ax.set_title(f"Purchase Heatmap - Iteration {current_grid_idx}")
            else:
                grid_ax.set_title(f"Walking Heatmap - Iteration {current_grid_idx}")
            
            # Update text labels
            update_text_labels()
            
            fig.canvas.draw_idle()

        # Mode change function
        def mode_change(label):
            nonlocal vis_mode
            
            if label == 'Layout':
                vis_mode = 'layout'
            elif label == 'Impulse Index':
                vis_mode = 'heatmap'
            elif label == 'Purchase Heatmap':
                vis_mode = 'purchases'
            else:  # 'Walking Heatmap'
                vis_mode = 'walking'
            
            # Update the visualization
            update(slider.val)
        
        slider.on_changed(update)
        radio.on_clicked(mode_change)
        
        # Add a highlight feature on mouse hover
        def hover(event):
            nonlocal highlighted_grid, last_hovered_aisle, grid_data
            
            if event.inaxes == grid_ax:
                x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
                if (0 <= y < grid_data.shape[0] and 0 <= x < grid_data.shape[1]):
                    aisle_id = grid_data[y, x]
                    
                    # Only do work if we're hovering over a different aisle than before
                    if aisle_id != last_hovered_aisle:
                        # Update title
                        if vis_mode == 'layout':
                            mode_prefix = "Layout"
                        elif vis_mode == 'heatmap':
                            mode_prefix = "Impulse Index Heatmap"
                        elif vis_mode == 'purchases':
                            mode_prefix = "Purchase Heatmap"
                        else:
                            mode_prefix = "Walking Heatmap"
                        grid_ax.set_title(f"{mode_prefix} - Iteration {current_grid_idx} - Aisle {aisle_id}")
                        
                        # Reset highlighted grid to original data
                        highlighted_grid = grid_data.copy()
                        
                        # Update info text with aisle data if available
                        if aisle_id > 0 and str(aisle_id) in self.aisle_info:
                            aisle_data = self.aisle_info[str(aisle_id)]
                            aisle_name = aisle_data.get('aisle_name', 'Unknown')
                            impulse_idx = aisle_data.get('impulse_index', 0)
                            product_count = aisle_data.get('product_count', 0)
                            
                            info_str = (f"Aisle ID: {aisle_id}\n\n"
                                    f"Name: {aisle_name}\n\n"
                                    f"Impulse Index: {impulse_idx:.3f}\n\n"
                                    f"Product Count: {product_count}")
                            
                            info_text.set_text(info_str)
                        else:
                            if aisle_id == 0:
                                info_text.set_text("Walkway\n\nPassage area for customers")
                            elif aisle_id == -1:
                                info_text.set_text("Exit\n\nStore exit point")
                            elif aisle_id == -2:
                                info_text.set_text("Entrance\n\nStore entrance point")  
                            else:
                                info_text.set_text(f"Aisle ID: {aisle_id}\n\nNo additional data available")
                        
                        # For layout mode, highlight cells with the same aisle ID
                        if vis_mode == 'layout' and aisle_id > 0:
                            # Gray out all non-walkable cells first
                            non_walkable_mask = (grid_data > 0)
                            highlighted_grid[non_walkable_mask] = max_aisle_id + 1  # Gray color

                            # Then highlight matching cells in orange
                            matching_mask = (grid_data == aisle_id)
                            highlighted_grid[matching_mask] = max_aisle_id + 0  # Orange color
                            
                            # Update the image data
                            im.set_array(highlighted_grid)
                        
                        # Remember which aisle we're hovering over
                        last_hovered_aisle = aisle_id
                        
                        # Trigger a redraw
                        fig.canvas.draw_idle()

        def on_leave(event):
            nonlocal highlighted_grid, last_hovered_aisle, grid_data
            
            if last_hovered_aisle is not None:
                # Reset the grid to original state
                if vis_mode == 'layout':
                    highlighted_grid = grid_data.copy()
                    im.set_array(highlighted_grid)
                    grid_ax.set_title(f"Layout - Iteration {current_grid_idx}")
                elif vis_mode == 'heatmap':
                    grid_ax.set_title(f"Impulse Index Heatmap - Iteration {current_grid_idx}")
                elif vis_mode == 'purchases':
                    grid_ax.set_title(f"Purchase Heatmap - Iteration {current_grid_idx}")
                else:
                    grid_ax.set_title(f"Walking Heatmap - Iteration {current_grid_idx}")
                    
                info_text.set_text("")
                last_hovered_aisle = None
                fig.canvas.draw_idle()
        
        fig.canvas.mpl_connect("motion_notify_event", hover)
        fig.canvas.mpl_connect("axes_leave_event", on_leave)
        
        plt.show()