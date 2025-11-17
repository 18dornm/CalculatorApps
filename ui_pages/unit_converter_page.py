from nicegui import ui
from ui_pages.unit_row import UnitRow
from calculators.unit_conversion import * 


def unit_converter_page():
    ui.label('Custom Conversion').classes('text-lg mt-6')
    UnitRow(all_units)

    ui.label('Force Conversion').classes('text-lg mt-6')
    UnitRow(force_units)

    ui.label('Torque Conversion').classes('text-lg mt-6')
    UnitRow(torque_units)

    ui.label('Pressure Conversion').classes('text-lg mt-6')
    UnitRow(pressure_units)

    ui.label('Length Conversion').classes('text-lg mt-6')
    UnitRow(length_units)

    ui.label('Mass Conversion').classes('text-lg mt-6')
    UnitRow(mass_units)

    ui.label('Speed Conversion').classes('text-lg mt-6')
    UnitRow(speed_units)

    ui.label('Acceleration Conversion').classes('text-lg mt-6')
    UnitRow(acceleration_units)

    ui.label('Second Moment of Area Conversion').classes('text-lg mt-6')
    UnitRow(second_moment_of_area_units)

    ui.label('Mass Moment of Inertia Conversion').classes('text-lg mt-6')
    UnitRow(moment_of_inertia_units)







