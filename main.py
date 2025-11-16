from nicegui import ui
from ui_pages.unit_converter_page import unit_converter_page

with ui.tabs() as tabs:
    tab_converter = ui.tab('Unit COnverter')
    tab_other = ui.tab('Other App')

with ui.tab_panels(tabs, value=tab_converter).classes('w-full'):
    with ui.tab_panel(tab_converter):
        unit_converter_page()
    
    with ui.tab_panel(tab_other):
        ui.label('Placeholder')
        ui.label('add next tool here')

ui.run()