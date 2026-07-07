# app.py
from nicegui import ui
import math
from main import start_polling, get_latest, RADIUS, LATITUDE, LONGITUDE
import os

host_port = 9090

# start_polling()

ui.dark_mode().enable()
ui.colors(primary="#890aff", secondary="#0935c7", dark='#111217')
ui.label('Custom Title')

with ui.grid(columns=3).classes('w-full gap-3 p-4'):
    with ui.card().classes('h-40 items-center justify-center'):
        ui.icon('flight', size='42px').classes('text-white')
        logo_label = ui.label('—').classes('panel-label')

        
def refresh():
    print(f'Latitude: {LATITUDE}')
    print(f'Longitude: {LONGITUDE}')
    print(f'Radius: {RADIUS}')
    

ui.timer(2.0, refresh)

ui.run(title='Aircraft Tracker', dark=True, show=False, port=host_port, favicon='✈')