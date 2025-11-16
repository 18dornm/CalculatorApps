from nicegui import ui
from ui_pages.unit_row import UnitRow

def unit_converter_page():
    
    ui.label('Force Conversion').classes('text-lg mt-6')
    UnitRow(['lbf', 'newton', 'kgf'])

    ui.label('Torque Conversion').classes('text-lg mt-6')
    UnitRow(['newton * meter', 'lbf * inch', 'lbf * foot', 'kgf * cm'])

    ui.label('Length Conversion').classes('text-lg mt-4')
    UnitRow(['millimeter', 'inch', 'meter', 'centimeter', 'foot', 'mile'])

    ui.label('Mass Conversion').classes('text-lg mt-6')
    UnitRow(['kilogram', 'gram', 'pound', 'ounce'])

    ui.label('Speed Conversion').classes('text-lg mt-6')
    UnitRow(['meter/second', 'kilometer/hour', 'mile/hour', 'foot/second'])





