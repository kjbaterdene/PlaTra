from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

import main as backend

backend.start_polling()

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


# ---------- Radar ----------

def build_radar_figure(planes, highlight_hex=None):
    nearby = [p for p in planes if p["distance_from_source"] <= 5]

    fig = go.Figure(
        go.Scatterpolar(
            r=[p["distance_from_source"] for p in nearby],
            theta=[p["bearing"] for p in nearby],
            mode="markers",
            marker=dict(
                color=[
                    "#ff4d4d" if p["hex"] == highlight_hex else "#4da6ff"
                    for p in nearby
                ],
                size=[
                    14 if p["hex"] == highlight_hex else 8
                    for p in nearby
                ],
            ),
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                showticklabels=False,
                gridcolor="#444",
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                showticklabels=False,
                gridcolor="#444",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
    )

    return fig


# ---------- Plane Card ----------

def build_plane_card(planes):
    if not planes:
        return dbc.Card(
            dbc.CardBody(
                html.H5("No aircraft nearby", className="text-center text-muted")
            ),
            className="bg-dark border-secondary",
        )

    closest = planes[0]

    flight = closest.get("flight", "").strip()

    logo = None
    if len(flight) >= 3 and flight[:3].isalpha():
        logo = (
            f"https://content.airhex.com/content/logos/"
            f"airlines_{flight[:3].upper()}_100_30_r.png"
        )

    radar = build_radar_figure(planes, closest["hex"])

    return dbc.Card(
        dbc.CardBody(
            [

                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src=logo,
                                style={
                                    "maxHeight": "45px",
                                    "maxWidth": "100%",
                                },
                            )
                            if logo
                            else html.Div(),
                            width=3,
                        ),

                        dbc.Col(
                            [
                                html.H4(
                                    closest.get("flight") or closest.get("r"),
                                    className="mb-0",
                                ),
                                html.Small(
                                    closest.get("t", ""),
                                    className="text-muted",
                                ),
                            ],
                            width=5,
                        ),

                        dbc.Col(
                            dcc.Graph(
                                figure=radar,
                                config={"displayModeBar": False},
                            ),
                            width=4,
                        ),
                    ],
                    className="align-items-center",
                ),

                html.Hr(),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    f"Distance: {closest['distance_from_source']:.2f} nm"
                                ),
                                html.Div(
                                    f"Heading: {closest.get('true_heading','N/A')}°"
                                ),
                            ]
                        ),

                        dbc.Col(
                            [
                                html.Div(f"Lat: {closest['lat']:.4f}"),
                                html.Div(f"Lon: {closest['lon']:.4f}"),
                            ]
                        ),

                        dbc.Col(
                            html.H3(
                                closest["compass"],
                                className="text-center text-info",
                            )
                        ),
                    ]
                ),

                html.Hr(),

                html.H5("Closest Aircraft"),

                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [
                                html.Span(
                                    p["flight"] or p["r"],
                                    className="fw-bold",
                                ),
                                html.Span(
                                    f"{p['distance_from_source']:.2f} nm",
                                    className="float-end",
                                ),
                            ],
                            color="dark",
                        )
                        for p in planes[:5]
                    ],
                    flush=True,
                ),
            ]
        ),
        className="bg-dark border-secondary shadow",
    )


# ---------- Layout ----------

app.layout = dbc.Container(
    [

        dbc.Row(
            [
                dbc.Col(
                    html.H1("Aircraft Tracker"),
                    width=8,
                ),
                dbc.Col(
                    html.Div(
                        id="last-updated",
                        className="text-end text-muted mt-3",
                    ),
                    width=4,
                ),
            ],
            className="mb-4",
        ),

        dbc.Row(
            [

                dbc.Col(
                    html.Div(id="plane-card-container"),
                    lg=4,
                ),

                dbc.Col(
                    dash_table.DataTable(
                        id="aircraft-table",
                        columns=[
                            {"name": "Flight", "id": "flight"},
                            {"name": "Lat", "id": "lat"},
                            {"name": "Lon", "id": "lon"},
                            {"name": "Heading", "id": "true_heading"},
                            {"name": "Distance", "id": "distance_from_source"},
                            {"name": "Compass", "id": "compass"},
                        ],
                        data=[],
                        page_size=12,
                        sort_action="native",
                        style_header={
                            "backgroundColor": "#222",
                            "color": "white",
                            "fontWeight": "bold",
                        },
                        style_cell={
                            "backgroundColor": "#111",
                            "color": "white",
                            "border": "1px solid #333",
                            "padding": "8px",
                            "textAlign": "center",
                        },
                        style_data_conditional=[
                            {
                                "if": {"row_index": "odd"},
                                "backgroundColor": "#181818",
                            },
                            {
                                "if": {
                                    "filter_query": "{distance_from_source} < 2"
                                },
                                "backgroundColor": "#4d1f1f",
                            },
                            {
                                "if": {
                                    "filter_query": "{distance_from_source} >= 2 && {distance_from_source} < 4"
                                },
                                "backgroundColor": "#4d3f1f",
                            },
                        ],
                    ),
                    lg=8,
                ),
            ]
        ),

        dcc.Interval(
            id="refresh",
            interval=3000,
            n_intervals=0,
        ),
    ],
    fluid=True,
    className="p-4",
)


# ---------- Callback ----------

@app.callback(
    Output("aircraft-table", "data"),
    Output("last-updated", "children"),
    Output("plane-card-container", "children"),
    Input("refresh", "n_intervals"),
)
def update_dashboard(_):
    planes, updated = backend.get_latest()

    return (
        planes,
        f"Last updated: {updated}" if updated else "Waiting for first update...",
        build_plane_card(planes),
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)