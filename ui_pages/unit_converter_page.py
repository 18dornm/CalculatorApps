from nicegui import ui
from ui_pages.unit_row import UnitRow
from calculators.unit_conversion import * 


def unit_converter_page():
    ui.label('Custom Conversion').classes('text-lg mt-6')
    UnitRow(all_units, True)

    ui.label('Force Conversion').classes('text-lg mt-6')
    UnitRow(force_units, False)

    ui.label('Torque Conversion').classes('text-lg mt-6')
    UnitRow(torque_units, False)

    ui.label('Pressure Conversion').classes('text-lg mt-6')
    UnitRow(pressure_units, False)

    ui.label('Length Conversion').classes('text-lg mt-6')
    UnitRow(length_units, False)

    ui.label('Mass Conversion').classes('text-lg mt-6')
    UnitRow(mass_units, False)

    ui.label('Speed Conversion').classes('text-lg mt-6')
    UnitRow(speed_units, False)

    ui.label('Acceleration Conversion').classes('text-lg mt-6')
    UnitRow(acceleration_units, False)

    ui.label('Second Moment of Area Conversion').classes('text-lg mt-6')
    UnitRow(second_moment_of_area_units, False)

    ui.label('Mass Moment of Inertia Conversion').classes('text-lg mt-6')
    UnitRow(moment_of_inertia_units, False)







