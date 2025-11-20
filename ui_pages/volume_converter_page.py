from nicegui import ui
from calculators.volume_conversion import *
from calculators.unit_conversion import pressure_units, volume_units, temperature_units

class VolumeConverterPage:
    def __init__(self):
        self.build_ui()

    def build_ui(self):
        ui.label('Volume Converter').classes('text-lg mt-6')
        with ui.row().classes('items-center gap-2'):
            self.volume_input = ui.number(label='Enter a Volume', value=1.0, on_change=self.update_output).classes('w-24')
            self.volume_input_unit = ui.select(options=volume_units,
                                        value=volume_units[0],
                                        with_input=True,
                                        new_value_mode='add-unique',
                                        on_change=self.update_output)
            ui.label("=")
            ui.button(icon='content_copy', on_click=self.copy_result).props('flat dense round size=sm').classes('bg-white text-black')
            self.volume_output = ui.label()
            self.volume_output_unit = ui.select(options=volume_units,
                                        value=volume_units[1],
                                        with_input=True,
                                        new_value_mode='add-unique',
                                        on_change=self.update_output)
        ui.separator()
        ui.label('Input Conditions').classes('text-lg mt-6')
        self.input_condition_type = ui.label('Conditions are Currently Custom.')
        with ui.row().classes('items-center gap-2'):
            ui.label('Set to...')
            ui.button('Standard Cubic Feet (US)', on_click=lambda: self.set_input_conditions(conditions_standard_cubic_feet, "Conditions are Currently Standard Cubic Feet (US)"))
            ui.button('ANR', on_click=lambda: self.set_input_conditions(conditions_anr_liters, "Conditions are Currently ANR Conditions"))
            ui.button('ISO 2533', on_click=lambda: self.set_input_conditions(conditions_ISO2533_liters, "Conditions are Currently ISO2533 Conditions"))
            ui.button('ISO 1217', on_click=lambda: self.set_input_conditions(conditions_ISO1217_liters, "Conditions are Currently ISO1217 Conditions"))
            ui.button('DIN 1343', on_click=lambda: self.set_input_conditions(conditions_DIN1343_liters, "Conditions are Currently DIN 1343 Conditions"))
        
        with ui.row().classes('items-center gap-2'):
            self.temperature_input = ui.number(label='Temperature', value=20.0, on_change=self.input_condition_changed).classes('w-24')
            self.temperature_input_unit = ui.select(options=temperature_units,
                                            value=temperature_units[0],
                                            with_input=True,
                                            on_change=self.input_condition_changed)
        with ui.row().classes('items-center gap-2'):
            self.pressure_input = ui.number(label='Gauge Pressure', value=80.0, on_change=self.input_condition_changed).classes('w-24')
            self.pressure_input_unit = ui.select(options=pressure_units,
                                            value='psi',
                                            with_input=True,
                                            on_change=self.input_condition_changed)
        with ui.row().classes('items-center gap-2'):
            self.pressure_atm_input = ui.number(label='Atmospheric Pressure', value=1.0, on_change=self.input_condition_changed).classes('w-24')
            self.pressure_atm_input_unit = ui.select(options=pressure_units,
                                            value='bar',
                                            with_input=True,
                                            on_change=self.input_condition_changed)
        with ui.row().classes('items-center gap-2'):
            self.RH_input = ui.number(label='Relative Humidity', value=0.0, min=0.0, max=100, on_change=self.input_condition_changed).classes('w-24')
            ui.label('%')
        
        ui.separator()
        ui.label('Output Conditions').classes('text-lg mt-6')
        self.output_condition_type = ui.label('Conditions are Currently Custom.')
        with ui.row().classes('items-center gap-2'):
            ui.label('Set to...')
            ui.button('Standard Cubic Feet (US)', on_click=lambda: self.set_output_conditions(conditions_standard_cubic_feet, "Conditions are Currently Standard Cubic Feet Conditions"))
            ui.button('ANR', on_click=lambda: self.set_output_conditions(conditions_anr_liters, "Conditions are Currently ANR Conditions"))
            ui.button('ISO 2533', on_click=lambda: self.set_output_conditions(conditions_ISO2533_liters, "Conditions are Currently ISO2533 Conditions"))
            ui.button('ISO 1217', on_click=lambda: self.set_output_conditions(conditions_ISO1217_liters, "Conditions are Currently ISO1217 Conditions"))
            ui.button('DIN 1343', on_click=lambda: self.set_output_conditions(conditions_DIN1343_liters, "Conditions are Currently DIN 1343 Conditions"))
        
        with ui.row().classes('items-center gap-2'):
            self.temperature_output = ui.number(label='Temperature', value=20.0, on_change=self.output_condition_changed).classes('w-24')
            self.temperature_output_unit = ui.select(options=temperature_units,
                                            value=temperature_units[0],
                                            with_input=True,
                                            new_value_mode='add',
                                            on_change=self.output_condition_changed)
        with ui.row().classes('items-center gap-2'):
            self.pressure_output = ui.number(label='Pressure', value=80.0, on_change=self.output_condition_changed).classes('w-24')
            self.pressure_output_unit = ui.select(options=pressure_units,
                                            value='psi',
                                            with_input=True,
                                            on_change=self.output_condition_changed)
        with ui.row().classes('items-center gap-2'):
            self.pressure_atm_output = ui.number(label='Atmospheric Pressure', value=1, on_change=self.output_condition_changed).classes('w-24')
            self.pressure_atm_output_unit = ui.select(options=pressure_units,
                                            value='bar',
                                            with_input=True,
                                            on_change=self.output_condition_changed)
        with ui.row().classes('items-center gap-2'):
            self.RH_output = ui.number(label='Relative Humidity', value=0.0, min=0.0, max=100, on_change=self.output_condition_changed).classes('w-24')
            ui.label('%')
    
    def update_output(self):
        Q = u.Quantity
        user_input_conditions = VolumeCondition(temperature=Q(self.temperature_input.value, self.temperature_input_unit.value),
                                                pressure_gauge=self.pressure_input.value*u(self.pressure_input_unit.value),
                                                pressure_atm_abs=self.pressure_atm_input.value*u(self.pressure_atm_input_unit.value),
                                                relative_humidity=self.RH_input.value/100)
        user_output_conditions = VolumeCondition(temperature=Q(self.temperature_output.value, self.temperature_output_unit.value),
                                                pressure_gauge=self.pressure_output.value*u(self.pressure_output_unit.value),
                                                pressure_atm_abs=self.pressure_atm_output.value*u(self.pressure_atm_output_unit.value),
                                                relative_humidity=self.RH_output.value/100)
        vol_in = self.volume_input.value * u(self.volume_input_unit.value) # make it a pint quantity with units
        vol_out = convert_volume(user_input_conditions, vol_in, user_output_conditions, True)
        vol = vol_out.to(self.volume_output_unit.value)
        self.volume_output.text = f"{vol.magnitude:.6f}"

    def input_condition_changed(self):
        self.input_condition_type.text = 'Conditions are Currently Custom.'
        self.update_output()

    def output_condition_changed(self):
        self.output_condition_type.text = 'Conditions are Currently Custom.'
        self.update_output()

    def set_input_conditions(self, condition: VolumeCondition, condition_type: str):
        self.temperature_input.value = condition.temperature.magnitude
        self.temperature_input_unit.value = f"{condition.temperature.units:~P}"
        self.pressure_input.value = condition.pressure_gauge.magnitude
        self.pressure_input_unit.value = f"{condition.pressure_gauge.units:~P}"
        self.pressure_atm_input.value = condition.pressure_atm_abs.magnitude
        self.pressure_atm_input_unit.value = f"{condition.pressure_atm_abs.units:~P}"
        self.RH_input.value = condition.relative_humidity * 100
        self.input_condition_type.text = condition_type # condition_type

    def set_output_conditions(self, condition: VolumeCondition, condition_type: str):
        self.temperature_output.value = condition.temperature.magnitude
        self.temperature_output_unit.value = f"{condition.temperature.units:~P}"
        self.pressure_output.value = condition.pressure_gauge.magnitude
        self.pressure_output_unit.value = f"{condition.pressure_gauge.units:~P}"
        self.pressure_atm_output.value = condition.pressure_atm_abs.magnitude
        self.pressure_atm_output_unit.value = f"{condition.pressure_atm_abs.units:~P}"
        self.RH_output.value = condition.relative_humidity * 100
        self.output_condition_type.text = condition_type # condition_type

    def copy_result(self):
        ui.run_javascript(f'navigator.clipboard.writeText("{self.volume_output.text}");')
        ui.notify('Copied to Clipboard', timeout=1)
        