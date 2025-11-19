from pint import UnitRegistry

u = UnitRegistry()

class VolumeCondition:
    def __init__(self, temperature, pressure_gauge, pressure_atm_abs, relative_humidity):
        self.temperature = temperature
        self.pressure_gauge = pressure_gauge
        self.pressure_atm_abs = pressure_atm_abs
        self.relative_humidity = relative_humidity


def convert_volume(input_conditions: VolumeCondition,
                   input_volume,
                   output_conditions:VolumeCondition,
                   consider_humidity:bool):
    if consider_humidity:
        input_vapor_partial_pressure = input_conditions.relative_humidity * saturation_pressure(input_conditions.temperature)
        output_vapor_partial_pressure = output_conditions.relative_humidity * saturation_pressure(output_conditions.temperature)
    else:
        input_vapor_partial_pressure = 0
        output_vapor_partial_pressure = 0
    
    # absolute pressures needed
    input_total_pressure = input_conditions.pressure_atm_abs + input_conditions.pressure_gauge
    output_total_pressure = output_conditions.pressure_atm_abs + output_conditions.pressure_gauge
    
    input_dry_partial_pressure = input_total_pressure - input_vapor_partial_pressure
    output_dry_partial_pressure = output_total_pressure - output_vapor_partial_pressure
    # converting to Pascals, not sure if this is necessary
    input_dry_partial_pressure = input_dry_partial_pressure.to('Pa')
    output_dry_partial_pressure = output_dry_partial_pressure.to('Pa')

    # absolute temperatures needed
    input_temperature = input_conditions.temperature.to('degK')
    output_temperature = output_conditions.temperature.to('degK')
    
    output_volume = input_volume * (input_dry_partial_pressure/output_dry_partial_pressure) * (output_temperature/input_temperature)
    return output_volume.to('m**3')


def saturation_pressure(temperature):
        """
        Calculate water vapor saturation pressure (kPa) using Antoine equation
        https://en.wikipedia.org/wiki/Antoine_equation
        
        Parameters:
        temperature: temperature (must be a pint quantity)
        
        Returns: saturation_pressure (as a pint quantity)
        """
        temp_C = temperature.to('degC')
        temp_C = temp_C.magnitude

        # Constants for water, valid from -20-100°C
        A = 8.07131
        B = 1730.63
        C = 233.426
        
        # Convert to pressure in kPa
        saturation_pressure_mmhg = 10**(A - (B / (C + temp_C)))
        saturation_pressure = saturation_pressure_mmhg * u('mmHg')
        return saturation_pressure

Q_ = u.Quantity
conditions_standard_cubic_feet = VolumeCondition(Q_(60, u.degF), 0*u('kPa'), 14.696*u('psi'), 0.0)
conditions_ISO2533_liters = VolumeCondition(Q_(15, u.degC), 0*u('kPa'), 1.01325*u('bar'), 0.0)
conditions_anr_liters = VolumeCondition(Q_(20, u.degC), 0*u('kPa'), 1.01325*u('bar'), 0.65)
conditions_ISO1217_liters = VolumeCondition(Q_(20, u.degC), 0.0*u('kPa'), 1.0*u('bar'), 0.0)
conditions_DIN1343_liters = VolumeCondition(Q_(0, u.degC), 0*u('kPa'), 101.325*u('kPa'), 0.0)

'''
# testing
test_input_conditions = VolumeCondition(Q_(72, u.degF), 80*u('psi'), 14.696*u('psi'), 0.35)
test_output_conditions = conditions_anr_liters
vol = 1 * u('ft**3')
vol_out = convert_volume(test_input_conditions, vol, test_output_conditions, True)
print(vol_out.to('liter'))
vol_out = convert_volume(test_input_conditions, vol, test_output_conditions, False)
print(vol_out.to('liter'))
'''