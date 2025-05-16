from dataclasses import dataclass
from optimization.tabu_search import Iteration
from typing import Dict, List
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

@dataclass
class CellVisData:
    aisle_id: int

@dataclass
class DashCellData:
    x: int
    y: int
    aisle_id: int
    text: str

@dataclass
class DashGridData:
    cells: List[DashCellData]
    unique_aisles: List[int]

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

    def get_data_for_dash(self) -> List[DashGridData]:
        """
        Prepare data for Dash: returns a list of dictionaries, one per iteration.
        Each dictionary contains:
        - 'cells': list of cell data (x, y, aisle_id, text)
        - 'unique_aisles': list of unique aisle_ids
        """
        all_data: List[DashGridData] = []

        # Get grid size from the first iteration
        rows = len(self.matrix_per_iteration[0])
        cols = len(self.matrix_per_iteration[0][0])

        for iteration_idx, matrix in enumerate(self.matrix_per_iteration):
            cells: List[DashCellData] = []
            unique_aisles = set()

            for i in range(rows):
                for j in range(cols):
                    cell = matrix[i][j]

                    cells.append(DashCellData(
                        x=j,
                        y=i,
                        aisle_id=cell.aisle_id,
                        text=f"Iteration: {iteration_idx}, Aisle ID: {cell.aisle_id}"
                    ))

                    unique_aisles.add(cell.aisle_id)

            all_data.append(DashGridData(
                cells=cells,
                unique_aisles=sorted(list(unique_aisles))
            ))

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
            all_unique_aisles.update(data.unique_aisles)
        all_unique_aisles = sorted(list(all_unique_aisles))

        # Map aisle IDs to colors
        aisle_colors: Dict[int, str]= {
            aisle: f'hsl({i * 360 / len(all_unique_aisles)}, 70%, 50%)'
            for i, aisle in enumerate(all_unique_aisles)
        }
        aisle_colors[0] = 'white'  # Pasillo color

        # Initial figure (show first iteration)
        initial_cells = all_data[0].cells
        initial_colors = [aisle_colors[cell.aisle_id] for cell in initial_cells]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[cell.x for cell in initial_cells],
            y=[cell.y for cell in initial_cells],
            mode='markers',
            marker=dict(size=10, color=initial_colors, showscale=False),
            text=[cell.text for cell in initial_cells],
            customdata=[cell.aisle_id for cell in initial_cells],
            hoverinfo='text',
            hovertemplate='<b>%{text}</b><extra></extra>'
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
            dcc.Store(id='console-logger'),
            html.Div(id='console-output', style={'display': 'none'}),
            dcc.Slider(
                id='iteration-slider',
                min=0,
                max=num_iterations - 1,
                value=0,
                marks={i: f"Iteration {i}" for i in range(num_iterations)}
            ),
            dcc.Graph(id='grid-plot', figure=fig)
        ])

        # app.clientside_callback(
        #     """
        #     function(data) {
        #         if(data) {
        #             console.log(data);
        #         }
        #         return null;
        #     }
        #     """,
        #     Output('console-output', 'children'),
        #     [Input('console-logger', 'data')]
        # )

        # Single callback to handle both slider and hover
        # @app.callback(
        #     [Output('grid-plot', 'figure'), 
        #         Output('console-logger', 'data')],
        #     [Input('iteration-slider', 'value'), 
        #         Input('grid-plot', 'hoverData')]
        # )

        @app.callback(
            Output('grid-plot', 'figure'),
            [Input('iteration-slider', 'value'), 
                Input('grid-plot', 'hoverData')]
        )
        def update_figure(iteration_idx: int, hoverData):
            # Determine which input triggered the callback
            ctx = dash.callback_context

            if not ctx.triggered:
                default_data = all_data[0]
                default_cells = default_data.cells
                default_colors = [aisle_colors[cell.aisle_id] for cell in default_cells]
                
                new_fig = go.Figure()
                new_fig.add_trace(go.Scatter(
                    x=[cell.x for cell in initial_cells],
                    y=[cell.y for cell in initial_cells],
                    mode='markers',
                    marker=dict(size=10, color=initial_colors, showscale=False),
                    text=[cell.text for cell in initial_cells],
                    customdata=[cell.aisle_id for cell in initial_cells],
                    hoverinfo='text',
                    hovertemplate='<b>%{text}</b><extra></extra>'
                ))

                return new_fig
            
            triggered_aisle_id: int = ctx.triggered[0]["value"]["points"][0]["customdata"]
            trigger_id: str = ctx.triggered[0]['prop_id'].split('.')[0]

            console_data = {
                'iteration': iteration_idx,
                'aisle_id': triggered_aisle_id,
                'context': 'Updating figure'
            }

            # Get the current data
            data = all_data[iteration_idx]
            cells = data.cells
            colors = [aisle_colors[cell.aisle_id] for cell in cells]

            # Create new figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[cell.x for cell in initial_cells],
                y=[cell.y for cell in initial_cells],
                mode='markers',
                marker=dict(size=10, color=initial_colors, showscale=False),
                customdata=[cell.aisle_id for cell in initial_cells],
                text=[cell.text for cell in initial_cells],
                hoverinfo='text',
                hovertemplate='<b>%{text}</b><extra></extra>'
            ))

            if triggered_aisle_id == 0:
                console_data['context'] = 'Hovering over aisle 0'
                return fig

            fig.update_layout(
                title=f"Interactive Grid - Iteration {iteration_idx}",
                xaxis_title="Columns",
                yaxis_title="Rows",
                width=600,
                height=600,
                xaxis=dict(tickmode='linear'),
                yaxis=dict(tickmode='linear')
            )

            # Highlight cells with the same aisle_id if hover is active
            if trigger_id == 'grid-plot' and hoverData:
                new_colors: List[str] = []
                for cell in cells:
                    if cell.aisle_id == triggered_aisle_id:
                        new_colors.append(aisle_colors[cell.aisle_id])
                    elif cell.aisle_id == 0:
                        new_colors.append('white')
                    else:
                        new_colors.append('lightgray')

                fig.data[0].update(marker=dict(color=new_colors))

            return fig

        # Run the Dash app
        app.run(debug=True)