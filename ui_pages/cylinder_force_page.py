from nicegui import ui
from calculators.unit_conversion import u, Q, length_units, pressure_units, force_units, area_units

class CylinderForcePage:
    def __init__(self):
        self.cylinder_diameter_qty = Q(20, 'mm')
        self.rod_diameter_qty = Q(8, 'mm')
        self.pressure_qty = Q(80, 'psi')
        self.build_ui()
        #self.calculate_force()

    def build_ui(self):
        with ui.card():
            ui.label('Inputs').classes('h1')
            with ui.row():
                self.cylinder_diameter = ui.number(label='Cylinder Diameter', value=20, min=0.0, on_change=self.calculate_force)
                self.cylinder_diameter_unit = ui.select(options=length_units, value='mm', on_change=self.calculate_force)
            
            with ui.row():
                self.rod_diameter = ui.number(label='Rod Diameter', value=8, min=0.0, on_change=self.calculate_force)
                self.rod_diameter_unit = ui.select(options=length_units, value='mm', on_change=self.calculate_force)
            
            with ui.row():
                self.pressure = ui.number(label='Cylinder Pressure', value=80, on_change=self.calculate_force)
                self.pressure_unit = ui.select(options=pressure_units, value='psi', on_change=self.calculate_force)
            
        ui.separator()
        with ui.card():
            ui.label("Outputs").classes('h1')
            with ui.row().classes('items-center gap-2'):
                ui.label("Extension Force = ")
                self.extend_force = ui.label()
                ui.button(icon='content_copy', on_click=lambda: self.copy_result(self.extend_force.text)).props('flat dense round size=sm').classes('bg-white text-black')
                self.extend_force_unit = ui.select(options=force_units, value='lbf', on_change = self.extend_force_unit_change)
            with ui.row().classes('items-center gap-2'):
                ui.label("Extension Area = ")
                self.extend_area = ui.label()
                ui.button(icon='content_copy', on_click=lambda: self.copy_result(self.extend_area.text)).props('flat dense round size=sm').classes('bg-white text-black')
                self.extend_area_unit = ui.select(options=area_units, value='mm²', on_change=self.extend_area_unit_change)
            with ui.row().classes('items-center gap-2'):
                ui.label("Retraction Force = ")
                self.retract_force = ui.label()
                ui.button(icon='content_copy', on_click=lambda: self.copy_result(self.retract_force.text)).props('flat dense round size=sm').classes('bg-white text-black')
                self.retract_force_unit = ui.select(options=force_units, value='lbf', on_change = self.retract_force_unit_change)
            with ui.row().classes('items-center gap-2'):
                ui.label("Retraction Area = ")
                self.retract_area = ui.label()
                ui.button(icon='content_copy', on_click=lambda: self.copy_result(self.retract_area.text)).props('flat dense round size=sm').classes('bg-white text-black')
                self.retract_area_unit = ui.select(options=area_units, value='mm²', on_change=self.retract_area_unit_change)
        self.calculate_force()
    
    def calculate_force(self):
        self.cylinder_diameter_qty = Q(self.cylinder_diameter.value, self.cylinder_diameter_unit.value)
        self.rod_diameter_qty = Q(self.rod_diameter.value, self.rod_diameter_unit.value)
        self.pressure_qty = Q(self.pressure.value, self.pressure_unit.value)
        
        self.extend_area_qty = ((self.cylinder_diameter_qty**2) * u.pi / 4)
        self.retract_area_qty = self.extend_area_qty - ((self.rod_diameter_qty**2) * u.pi / 4)
        self.extend_force_qty = self.pressure_qty * self.extend_area_qty
        self.retract_force_qty = self.pressure_qty * self.retract_area_qty

        self.extend_force_qty = self.extend_force_qty.to(self.extend_force_unit.value)
        self.retract_force_qty = self.retract_force_qty.to(self.retract_force_unit.value)
        self.extend_area_qty = self.extend_area_qty.to(self.extend_area_unit.value)
        self.retract_area_qty = self.retract_area_qty.to(self.retract_area_unit.value)
        
        self.extend_force.text = f"{self.extend_force_qty.magnitude:0.4f}"
        self.extend_area.text = f"{self.extend_area_qty.magnitude:0.4f}"
        self.retract_force.text = f"{self.retract_force_qty.magnitude:0.4f}"
        self.retract_area.text = f"{self.retract_area_qty.magnitude:0.4f}"

    def extend_force_unit_change(self):
        self.extend_force_qty = self.extend_force_qty.to(self.extend_force_unit.value)
        self.extend_force.text = f"{self.extend_force_qty.magnitude:0.4f}"

    def extend_area_unit_change(self):
        self.extend_area_qty = self.extend_area_qty.to(self.extend_area_unit.value)
        self.extend_area.text = f"{self.extend_area_qty.magnitude:0.4f}"
    
    def retract_force_unit_change(self):
        self.retract_force_qty = self.retract_force_qty.to(self.retract_force_unit.value)
        self.retract_force.text = f"{self.retract_force_qty.magnitude:0.4f}"

    def retract_area_unit_change(self):
        self.retract_area_qty = self.retract_area_qty.to(self.retract_area_unit.value)
        self.retract_area.text = f"{self.retract_area_qty.magnitude:0.4f}"

    def copy_result(self, text):
        ui.run_javascript(f'navigator.clipboard.writeText("{text}");')
        ui.notify('Copied to Clipboard', timeout=1)