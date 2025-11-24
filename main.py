from nicegui import ui
from ui_pages.unit_converter_page import unit_converter_page
from ui_pages.volume_converter_page import VolumeConverterPage
from ui_pages.beam_calculator_page import BeamCalculatorPage

with ui.tabs() as tabs:
    tab_converter = ui.tab('Unit Converter')
    tab_volume_converter = ui.tab('Volume Converter')
    tab_beam_calculator = ui.tab('Beam Calculator')

with ui.tab_panels(tabs, value=tab_converter).classes('w-full'):
    with ui.tab_panel(tab_converter):
        unit_converter_page()
    
    with ui.tab_panel(tab_volume_converter):
        VolumeConverterPage()
    
    with ui.tab_panel(tab_beam_calculator):
        BeamCalculatorPage()

ui.run(title='Calculator Apps', host='0.0.0.0', port=7860)