from nicegui import ui
from calculators.volume_conversion import *
from calculators.unit_conversion import pressure_units, volume_units, temperature_units

def volume_converter_page():
    def update_output():
        temp = u.Quantity
        user_input_conditions = VolumeCondition(temperature=temp(temperature_input.value, temperature_output_unit.value),
                                                pressure_gauge=pressure_input.value*u(pressure_input_unit.value),
                                                pressure_atm_abs=pressure_atm_input.value*u(pressure_atm_input_unit.value),
                                                relative_humidity=RH_input.value/100)
        user_output_conditions = VolumeCondition(temperature=temp(temperature_output.value, temperature_output_unit.value),
                                                pressure_gauge=pressure_output.value*u(pressure_output_unit.value),
                                                pressure_atm_abs=pressure_atm_output.value*u(pressure_atm_output_unit.value),
                                                relative_humidity=RH_output.value/100)
        vol_in = volume_input.value * u(volume_input_unit.value) # make it a pint quantity with units
        vol_out = convert_volume(user_input_conditions, vol_in, user_output_conditions, True)
        vol = vol_out.to(volume_output_unit.value)
        volume_output.text = f"{vol.magnitude:.6f}"

    def input_condition_changed():
        input_condition_type.text = 'Custom Conditions'
        update_output()

    def output_condition_changed():
        output_condition_type.text = 'Custom Conditions'
        update_output()

    def set_input_conditions(condition: VolumeCondition, condition_type: str):
        #input_condition_type.text = condition_type
        #temperature_input.value = condition.temperature
        return 0

    def set_output_conditions(condition: VolumeCondition, condition_type: str):
        #TODO
        return 0

    def copy_result(self):
        ui.run_javascript(f'navigator.clipboard.writeText("{volume_output.text}");')
        ui.notify('Copied to Clipboard', timeout=1)


    
    ui.label('Volume Converter').classes('text-lg mt-6')
    with ui.row().classes('items-center gap-2'):
        volume_input = ui.number(label='Enter a Volume', value=1.0, on_change=update_output).classes('w-24')
        volume_input_unit = ui.select(options=volume_units,
                                      value=volume_units[0],
                                      with_input=True,
                                      new_value_mode='add-unique',
                                      on_change=update_output)
        ui.label("=")
        ui.button(icon='content_copy', on_click=copy_result).props('flat dense round size=sm').classes('bg-white text-black')
        volume_output = ui.label()
        volume_output_unit = ui.select(options=volume_units,
                                      value=volume_units[1],
                                      with_input=True,
                                      new_value_mode='add-unique',
                                      on_change=update_output)
    ui.separator()
    ui.label('Input Conditions').classes('text-lg mt-6')
    with ui.row().classes('items-center gap-2'):
        ui.label('Set to...')
        ui.button('Standard Cubic Feet (US)', on_click=set_input_conditions(conditions_standard_cubic_feet, "Standard Cubic Feet Conditions"))
        ui.button('ANR', on_click=set_input_conditions(conditions_anr_liters, "ANR Conditions"))
        ui.button('ISO 2533', on_click=set_input_conditions(conditions_ISO2533_liters, "ISO2533 Conditions"))
        ui.button('ISO 1217', on_click=set_input_conditions(conditions_ISO1217_liters, "ISO1217 Conditions"))
        ui.button('DIN 1343', on_click=set_input_conditions(conditions_DIN1343_liters, "DIN 1343 Conditions"))
    input_condition_type = ui.label('Custom Conditions')
    with ui.row().classes('items-center gap-2'):
        temperature_input = ui.number(label='Temperature', value=20.0, on_change=input_condition_changed).classes('w-24')
        temperature_input_unit = ui.select(options=temperature_units,
                                        value=temperature_units[0],
                                        with_input=True,
                                        on_change=input_condition_changed)
    with ui.row().classes('items-center gap-2'):
        pressure_input = ui.number(label='Gauge Pressure', value=80.0, on_change=input_condition_changed).classes('w-24')
        pressure_input_unit = ui.select(options=pressure_units,
                                        value='psi',
                                        with_input=True,
                                        on_change=input_condition_changed)
    with ui.row().classes('items-center gap-2'):
        pressure_atm_input = ui.number(label='Atmospheric Pressure', value=1.0, on_change=input_condition_changed).classes('w-24')
        pressure_atm_input_unit = ui.select(options=pressure_units,
                                        value='bar',
                                        with_input=True,
                                        on_change=input_condition_changed)
    with ui.row().classes('items-center gap-2'):
        RH_input = ui.number(label='Relative Humidity', value=0.0, min=0.0, max=100, on_change=input_condition_changed).classes('w-24')
        ui.label('%')
    
    ui.separator()
    ui.label('Output Conditions').classes('text-lg mt-6')
    with ui.row().classes('items-center gap-2'):
        ui.label('Set to...')
        ui.button('Standard Cubic Feet (US)', on_click=set_output_conditions(conditions_standard_cubic_feet, "Standard Cubic Feet Conditions"))
        ui.button('ANR', on_click=set_output_conditions(conditions_anr_liters, "ANR Conditions"))
        ui.button('ISO 2533', on_click=set_output_conditions(conditions_ISO2533_liters, "ISO2533 Conditions"))
        ui.button('ISO 1217', on_click=set_output_conditions(conditions_ISO1217_liters, "ISO1217 Conditions"))
        ui.button('DIN 1343', on_click=set_output_conditions(conditions_DIN1343_liters, "DIN 1343 Conditions"))
    output_condition_type = ui.label('Custom Conditions')
    with ui.row().classes('items-center gap-2'):
        temperature_output = ui.number(label='Temperature', value=20.0, on_change=output_condition_changed).classes('w-24')
        temperature_output_unit = ui.select(options=temperature_units,
                                        value=temperature_units[0],
                                        with_input=True,
                                        on_change=output_condition_changed)
    with ui.row().classes('items-center gap-2'):
        pressure_output = ui.number(label='Pressure', value=80.0, on_change=output_condition_changed).classes('w-24')
        pressure_output_unit = ui.select(options=pressure_units,
                                        value='psi',
                                        with_input=True,
                                        on_change=output_condition_changed)
    with ui.row().classes('items-center gap-2'):
        pressure_atm_output = ui.number(label='Atmospheric Pressure', value=1, on_change=output_condition_changed).classes('w-24')
        pressure_atm_output_unit = ui.select(options=pressure_units,
                                        value='bar',
                                        with_input=True,
                                        on_change=output_condition_changed)
    with ui.row().classes('items-center gap-2'):
        RH_output = ui.number(label='Relative Humidity', value=0.0, min=0.0, max=100, on_change=output_condition_changed).classes('w-24')
        ui.label('%')

    update_output()