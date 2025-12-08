from nicegui import ui

ui.colors(
    primary="#3448b9",
    secondary="#5b7196",
    accent='#7c4dff',
    dark='#28262C',
    positive='#21BA45',
    negative="#B93F4D",
    warning="#F0C245",
    info="#41C6E0",
)
ui.add_head_html("""
<style>
  .h1 { font-size: 1.25rem; font-weight: 500; color: var(--q-primary); }
  .h2 { font-size: 1.0rem; font-weight: 500; color: var(--q-dark); }
  .h3 { font-size: 0.75rem; font-weight: 300; color: var(--q-primary); }
  .body-text { font-size: 1rem; font-weight: 300; color: grey-800; }
  .table-header {
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: .02em;
      color: var(--q-secondary);
  }
</style>
""")

from ui_pages.unit_converter_page import unit_converter_page
from ui_pages.volume_converter_page import VolumeConverterPage
from ui_pages.beam_calculator_page import BeamCalculatorPage
from ui_pages.cylinder_force_page import CylinderForcePage




with ui.tabs() as tabs:
    tab_converter = ui.tab('Unit Converter')
    tab_volume_converter = ui.tab('Volume Converter')
    tab_beam_calculator = ui.tab('Beam Calculator')
    tab_cylinder_force = ui.tab('Cylinder Force')

with ui.tab_panels(tabs, value=tab_converter).classes('w-full'):
    with ui.tab_panel(tab_converter):
        unit_converter_page()
    
    with ui.tab_panel(tab_volume_converter):
        VolumeConverterPage()
    
    with ui.tab_panel(tab_beam_calculator):
        BeamCalculatorPage()
    
    with ui.tab_panel(tab_cylinder_force):
        CylinderForcePage()

ui.run(title='Calculator Apps', host='0.0.0.0', port=7860)