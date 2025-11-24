from nicegui import ui
from ui_pages.unit_row import UnitRow
from calculators.unit_conversion import * 


def unit_converter_page():
    ui.label('Custom Conversion').classes('text-lg mt-6')
    UnitRow(all_units, True)
    ui.separator()

    ui.label('Other Conversions').classes('text-lg mt-6')

    ui.label('Force Conversion')
    UnitRow(force_units, False)
    
    ui.label('Torque Conversion')
    UnitRow(torque_units, False)
    
    ui.label('Pressure Conversion')
    UnitRow(pressure_units, False)
    
    ui.label('Length Conversion')
    UnitRow(length_units, False)
    
    ui.label('Mass Conversion')
    UnitRow(mass_units, False)
    
    ui.label('Speed Conversion')
    UnitRow(speed_units, False)
    
    ui.label('Acceleration Conversion')
    UnitRow(acceleration_units, False)
    
    ui.label('Second Moment of Area Conversion')
    UnitRow(second_moment_of_area_units, False)
    
    ui.label('Mass Moment of Inertia Conversion')
    UnitRow(moment_of_inertia_units, False)
    






