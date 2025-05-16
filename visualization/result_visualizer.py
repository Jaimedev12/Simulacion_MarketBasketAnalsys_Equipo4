from dataclasses import dataclass
from optimization.tabu_search import Iteration
from typing import List
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

@dataclass
class CellVisData:
    aisle_id: int

class ResultVisualizer:
    def __init__(self, iterations: List[Iteration]):
        self.iterations: List[Iteration] = iterations
        self.matrix_per_iteration: List[List[List[CellVisData]]] = []
        self._initialize_matrices()

    def _initialize_matrices(self):
        """
        Initialize a matrix for each iteration.
        """
        if not self.iterations:
            return

        # Get grid size from the first iteration
        rows = self.iterations[0].grid.rows
        cols = self.iterations[0].grid.cols

        # Initialize a list of matrices (one per iteration)
        self.matrix_per_iteration = [
            [[CellVisData(0) for _ in range(cols)] for _ in range(rows)]
            for _ in range(len(self.iterations))
        ]

        # Fill each matrix with data from the corresponding iteration
        for idx, it in enumerate(self.iterations):
            for i, row in enumerate(it.grid.grid):
                for j, cell in enumerate(row):
                    self.matrix_per_iteration[idx][i][j].aisle_id = cell.aisle_id

    def get_data_for_dash(self):
        """
        Prepare data for Dash: returns a list of dictionaries, one per iteration.
        Each dictionary contains:
        - 'cells': list of cell data (x, y, aisle_id, text)
        - 'unique_aisles': list of unique aisle_ids
        """
        all_data = []

        # Get grid size from the first iteration
        rows = len(self.matrix_per_iteration[0])
        cols = len(self.matrix_per_iteration[0][0])

        for iteration_idx, matrix in enumerate(self.matrix_per_iteration):
            cells = []
            unique_aisles = set()

            for i in range(rows):
                for j in range(cols):
                    cell = matrix[i][j]
                    cells.append({
                        'x': j,
                        'y': i,
                        'aisle_id': cell.aisle_id,
                        'text': f"Iteration: {iteration_idx}, Aisle ID: {cell.aisle_id}"
                    })
                    unique_aisles.add(cell.aisle_id)

            all_data.append({
                'cells': cells,
                'unique_aisles': sorted(list(unique_aisles))
            })

        return all_data
    
    def visualize(self):
        """
        Launch an interactive visualization using Dash.
        """
        # Get data for all iterations
        all_data = self.get_data_for_dash()
        num_iterations = len(all_data)

        if num_iterations == 0:
            print("No iterations to visualize.")
            return

        # Extract unique aisle IDs across all iterations
        all_unique_aisles = set()
        for data in all_data:
            all_unique_aisles.update(data['unique_aisles'])
        all_unique_aisles = sorted(list(all_unique_aisles))

        # Map aisle IDs to colors
        aisle_colors = {
            aisle: f'hsl({i * 360 / len(all_unique_aisles)}, 70%, 50%)'
            for i, aisle in enumerate(all_unique_aisles)
        }
        aisle_colors[0] = 'white'  # Default color for aisle_id 0 (pasillo)

        # Initial figure (show first iteration)
        initial_cells = all_data[0]['cells']
        initial_colors = [aisle_colors[cell['aisle_id']] for cell in initial_cells]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[cell['x'] for cell in initial_cells],
            y=[cell['y'] for cell in initial_cells],
            mode='markers',
            marker=dict(size=10, color=initial_colors, showscale=False),
            text=[cell['text'] for cell in initial_cells],
            hoverinfo='text'
        ))

        fig.update_layout(
            title="Interactive Grid with Aisle ID Highlights",
            xaxis_title="Columns",
            yaxis_title="Rows",
            width=600,
            height=600,
            xaxis=dict(tickmode='linear'),
            yaxis=dict(tickmode='linear')
        )

        # Create Dash app
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Slider(
                id='iteration-slider',
                min=0,
                max=num_iterations - 1,
                value=0,
                marks={i: f"Iteration {i}" for i in range(num_iterations)}
            ),
            dcc.Graph(id='grid-plot', figure=fig)
        ])

        @app.callback(
            Output('grid-plot', 'figure'),
            [Input('iteration-slider', 'value')]
        )
        def update_figure(iteration_idx):
            # Get data for the selected iteration
            data = all_data[iteration_idx]
            cells = data['cells']

            # Assign colors based on aisle_id
            colors = [aisle_colors[cell['aisle_id']] for cell in cells]

            # Create new figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[cell['x'] for cell in cells],
                y=[cell['y'] for cell in cells],
                mode='markers',
                marker=dict(size=10, color=colors, showscale=False),
                text=[cell['text'] for cell in cells],
                hoverinfo='text'
            ))

            fig.update_layout(
                title=f"Interactive Grid - Iteration {iteration_idx}",
                xaxis_title="Columns",
                yaxis_title="Rows",
                width=600,
                height=600,
                xaxis=dict(tickmode='linear'),
                yaxis=dict(tickmode='linear')
            )

            return fig

        # Run the Dash app
        app.run(debug=True)