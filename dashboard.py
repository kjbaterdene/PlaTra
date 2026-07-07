# app.py
from nicegui import ui
import math
from datetime import datetime
from main import start_polling, get_latest

start_polling()

ui.dark_mode().enable()
ui.colors(primary="#7806bb", secondary='#73bf69', dark='#111217')

ui.add_head_html('''
<style>
body { background-color: #111217 !important; }
.q-card {
    background-color: #181b1f !important;
    border: 1px solid #2c3235 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}
.panel-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #8e8e8e;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 15px;
    font-weight: 600;
    color: #d8d9da;
    font-family: 'Roboto Mono', monospace;
}
.big-heading {
    font-size: 56px;
    font-weight: 700;
    color: #73bf69;
    font-family: 'Roboto Mono', monospace;
}
.q-table { background-color: #181b1f !important; color: #d8d9da !important; }
.q-table th {
    background-color: #1f1f23 !important;
    color: #8e8e8e !important;
    text-transform: uppercase;
    font-size: 11px;
}
</style>
''')

RANGE_NM = 5  # matches tracker.py RADIUS


def build_radar_svg(planes):
    size = 280
    center = size / 2
    max_r = center - 30

    rings = ''
    for i in range(1, RANGE_NM + 1):
        r = max_r * i / RANGE_NM
        rings += f'<circle cx="{center}" cy="{center}" r="{r}" fill="none" stroke="#2c3235" stroke-width="1"/>'

    # ring distance labels along one spoke only, spaced so they don't collide
    for i in range(1, RANGE_NM + 1):
        r = max_r * i / RANGE_NM
        rings += f'<text x="{center + 3}" y="{center - r - 2}" fill="#555" font-size="9">{i}</text>'

    # compass labels at the outer edge, one per direction, not stacked
    compass_points = {'N': (center, 14), 'E': (size - 14, center), 'S': (center, size - 6), 'W': (14, center)}
    for label, (x, y) in compass_points.items():
        rings += f'<text x="{x}" y="{y}" fill="#666" font-size="11" text-anchor="middle">{label}</text>'

    crosshair = (
        f'<line x1="{center}" y1="30" x2="{center}" y2="{size-30}" stroke="#2c3235"/>'
        f'<line x1="30" y1="{center}" x2="{size-30}" y2="{center}" stroke="#2c3235"/>'
        f'<circle cx="{center}" cy="{center}" r="4" fill="#ff780a"/>'
    )

    planes_svg = ''

    if planes:
        p = planes[0]  # closest plane

        dist = min(p['distance_from_source'], RANGE_NM)
        bearing = p['bearing']

        r = max(max_r * dist / RANGE_NM, 14)
        rad = math.radians(bearing)

        x = center + r * math.sin(rad)
        y = center - r * math.cos(rad)

        heading = p.get('true_heading') or bearing

        planes_svg = (
            f'<g transform="translate({x},{y}) rotate({heading})">'
            f'<path d="M0,-7 L4,5 L0,2 L-4,5 Z" fill="#73bf69"/>'
            f'</g>'
        )
    return f'''
    <svg
        viewBox="0 0 {size} {size}"
        width="100%"
        height="100%"
        preserveAspectRatio="xMidYMid meet">
        {rings}
        {crosshair}
        {planes_svg}
    </svg>
    '''

# Build page
with ui.grid(columns=3).classes('w-full gap-3 p-4'):
    with ui.card().classes('items-center justify-center'):
        ui.label('AIRLINE').classes('panel-label')
        ui.icon('flight', size='42px').classes('text-white')
        logo_label = ui.label('—').classes('panel-label')

    with ui.card():
        ui.label('POSITION').classes('panel-label')
        lat_label = ui.label('Lat: —').classes('metric-value')
        lon_label = ui.label('Lon: —').classes('metric-value')
        spd_label = ui.label('Speed: —').classes('metric-value')
        alt_label = ui.label('Alt: —').classes('metric-value')

# Radar card, depricated bc it doesn't look good with slow updates
    """ with ui.card().classes('items-center justify-center p-2'):
        radar_html = ui.html(build_radar_svg([])) """
    with ui.card():
        ui.label('ATC').classes('panel-label')


    with ui.card():
        ui.label('IDENTIFICATION').classes('panel-label')
        reg_label = ui.label('Reg: —').classes('metric-value')
        flight_label = ui.label('Flight: —').classes('metric-value')

    with ui.card():
        ui.label('AIRCRAFT').classes('panel-label')
        model_label = ui.label('Model: —').classes('metric-value')
        mfr_label = ui.label('Mfr: —').classes('metric-value')
        eng_label = ui.label('Engine: —').classes('metric-value')

    with ui.card().classes('items-center justify-center'):
        ui.label('LOOK').classes('panel-label')
        heading_label = ui.label('N').classes('big-heading')

    with ui.card().classes('col-span-3'):
        ui.label('5 CLOSEST AIRCRAFT').classes('panel-label')
        columns = [
            {'name': 'flight', 'label': 'Flight', 'field': 'flight', 'align': 'left'},
            {'name': 'r', 'label': 'Reg', 'field': 'r', 'align': 'left'},
            {'name': 'name', 'label': 'Aircraft', 'field': 'name', 'align': 'left'},
            {'name': 'distance_from_source', 'label': 'Dist (nm)', 'field': 'distance_from_source'},
            {'name': 'compass', 'label': 'Dir', 'field': 'compass'},
        ]
        table = ui.table(columns=columns, rows=[], row_key='hex').classes('w-full')


def refresh():
    planes, updated_at = get_latest()

# Radar card, depricated bc it doesn't look good with slow updates
    """ radar_html.content = build_radar_svg(planes)
    radar_html.update() """

    if planes:
        closest = planes[0]
        pd = closest.get('plane_data') or {}

        logo_label.text = closest.get('flight') or closest.get('r') or '—'
        lat_label.text = f"Latitude: {closest['lat']:.4f}"
        lon_label.text = f"Longitude: {closest['lon']:.4f}"
        spd_label.text = f"Speed: {closest.get('speed', '—')} kt"
        alt_label.text = f"Altitude: {closest.get('altitude')} ft" if closest.get('altitude') != 'ground' else 'Altitude: Grounded'

        reg_label.text = f"Reg: {closest.get('r') or '—'}"
        flight_label.text = f"Flight: {closest.get('flight') or '—'}"

        model_label.text = f"Model: {pd.get('name', '—').title() or '—'}"
        mfr_label.text = f"Manufacturer: {pd.get('manufacturer', '—') or '—'}"
        eng_label.text = f"Engine: {pd.get('engine', '—') or '—'}"

        heading_label.text = closest.get('compass', 'N')

    rows = []
    for p in planes[:5]:
        row = dict(p)
        pd = p.get('plane_data') or {}
        row['name'] = pd.get('name', '—')
        rows.append(row)
    table.rows = rows
    table.update()


ui.timer(2.0, refresh)

ui.run(title='Aircraft Tracker', dark=True, show=False)