from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output

import main as backend

backend.start_polling()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Aircraft Tracker"),
    html.Div(id="last-updated"),
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
    ),
    dcc.Interval(id="refresh", interval=3000, n_intervals=0)
])

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