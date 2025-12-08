from nicegui import ui
from ui_pages.unit_row import UnitRow
from calculators.unit_conversion import * 


def unit_converter_page():
    ui.label('Custom Conversion').classes('h1')
    with ui.card():
        UnitRow(all_units, True)
    ui.separator()

    ui.label('Other Conversions').classes('h1')

    with ui.card():
        ui.label('Force Conversion').classes('h2')
        UnitRow(force_units, False)
    with ui.card():
        ui.label('Torque Conversion').classes('h2')
        UnitRow(torque_units, False)
    with ui.card():
        ui.label('Pressure Conversion').classes('h2')
        UnitRow(pressure_units, False)
    with ui.card():
        ui.label('Length Conversion').classes('h2')
        UnitRow(length_units, False)
    with ui.card():
        ui.label('Mass Conversion').classes('h2')
        UnitRow(mass_units, False)
    with ui.card():
        ui.label('Speed Conversion').classes('h2')
        UnitRow(speed_units, False)
    with ui.card():
        ui.label('Acceleration Conversion').classes('h2')
        UnitRow(acceleration_units, False)
    with ui.card():
        ui.label('Second Moment of Area Conversion').classes('h2')
        UnitRow(second_moment_of_area_units, False)
    with ui.card():
        ui.label('Mass Moment of Inertia Conversion').classes('h2')
        UnitRow(moment_of_inertia_units, False)
    






