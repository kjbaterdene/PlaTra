from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import main as backend

backend.start_polling()

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H1("Aircraft Tracker", className="my-4"), width=8),
        dbc.Col(html.Div(id="last-updated", className="my-4 text-end text-muted"), width=4),
    ]),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Nearby Aircraft"),
                dbc.CardBody(
                    dash_table.DataTable(
                        id="aircraft-table",
                        columns=[
                            {"name": "Flight", "id": "flight"},
                            {"name": "Lat", "id": "lat"},
                            {"name": "Lon", "id": "lon"},
                            {"name": "Altitude", "id": "alt_baro"},
                            {"name": "Distance (nm)", "id": "distance_from_source"},
                        ],
                        data=[],
                        style_header={
                            "backgroundColor": "#1a1a1a",
                            "color": "white",
                            "fontWeight": "bold",
                            "border": "1px solid #333",
                        },
                        style_cell={
                            "backgroundColor": "#111",
                            "color": "white",
                            "border": "1px solid #333",
                            "padding": "8px",
                        },
                        style_data_conditional=[
                            {"if": {"row_index": "odd"}, "backgroundColor": "#1e1e1e"},
                            {
                                "if": {"filter_query": "{distance_from_source} < 2"},
                                "backgroundColor": "#4a1f1f",
                            },
                            {
                                "if": {
                                    "filter_query": "{distance_from_source} >= 2 && {distance_from_source} < 4"
                                },
                                "backgroundColor": "#4a3f1f",
                            },
                        ],
                        style_table={"overflowX": "auto"},
                    )
                ),
            ]),
            width=12,
        ),
    ]),

    dcc.Interval(id="refresh", interval=3000, n_intervals=0),

], fluid=True, className="p-4")


@app.callback(
    Output("aircraft-table", "data"),
    Output("last-updated", "children"),
    Input("refresh", "n_intervals")
)
def update_table(n):
    planes, updated_at = backend.get_latest()
    return planes, f"Last updated: {updated_at}"


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)