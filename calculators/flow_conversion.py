from pint import UnitRegistry

u = UnitRegistry()
R = 287.058  # Gas constant for air, J/(kg·K)

class VolumeCondition:
    def __init__(
        self,
        temp_C: float,
        pressure_gauge_kPa: float,
        pressure_atmospheric_absolute_kPa: float = 101.325,
        relative_humidity: float = 0.0
    ):
        self.temp_C = temp_C
        self.pressure_gauge_kPa = pressure_gauge_kPa
        self.pressure_atmospheric_absolute_kPa = pressure_atmospheric_absolute_kPa
        self.relative_humidity = relative_humidity


conditions_standard_cubic_feet = VolumeCondition(u.convert(68, 'degF', 'degC'), 0.0, 101.325, 0.0)
conditions_standard_liters = VolumeCondition(20.0, 0.0, 101.325, 0.0)
conditions_anr_liters = VolumeCondition(20.0, 0.0, 100.0, 0.65)
conditions_ISO1217_liters = VolumeCondition(20.0, 0.0, 100.0, 0.0)
conditions_normal_liters = VolumeCondition(0.0, 0.0, 101.325, 0.0)

def convert_volumes(volume_m3: float, input_conditions: VolumeCondition, output_conditions: VolumeCondition, consider_humidity: bool):
    '''
    Convert volumes between different flow conditions
    Parameters:
    volume_m3: Volume in cubic meters
    input_conditions, output_conditons: VolumeCondition objects
    Returns: dictionary of converted volumes
    '''
    # calculate the mass of the air in the volume
    pressure_abs_input_kPa = input_conditions.pressure_gauge_kPa + 
    # calculate the effective pressure based on humidity
    T_output_K = u.convert(output_conditions.temp_C, 'degC', 'degK')
    P_abs_output_kPa = output_conditions.pressure_atmospheric_absolute_kPa + output_conditions.pressure_gauge_kPa
    if consider_humidity:
          P_water_output_kPa = output_conditions.relative_humidity * saturation_pressure_kPa(output_conditions.temp_C)
    else:
         P_water_output_kPa = 0.0
    P_dry_output_kPa = P_abs_output_kPa - P_water_output_kPa
    volume_output = mass_output_kg * R * T_output_K / P_dry_output_kPa
    

def saturation_pressure_kPa(temp_C):
        """
        Calculate water vapor saturation pressure (kPa) using Antoine equation
        https://en.wikipedia.org/wiki/Antoine_equation
        
        Parameters:
        temp_C: temp in Celsius
        
        Returns: Saturation pressure in kPa
        """
        # Constants for water, valid from 1-100°C
        A = 8.07131
        B = 1730.63
        C = 233.426
        
        # Convert to pressure in kPa
        saturation_pressure_mmhg = 10**(A - (B / (C + temp_C)))
        return u.convert(saturation_pressure_mmhg, 'mmHg', 'kPa')


def find_mass(conditions:VolumeCondition, volume_m3:float, consider_humidity:bool):
        temp_K = u.convert(conditions.temp_C, 'degC', 'degK')
        
		# Add atmospheric pressure to gauge pressure to get absolute pressure
        pressure_abs_kPa = conditions.pressure_gauge_kPa + conditions.pressure_atmospheric_absolute_kPa
        
        
        # Calculate effective pressure based on humidity consideration
        if consider_humidity:
            # Calculate water vapor partial pressure
            P_sat_kPa = saturation_pressure_kPa(conditions.temp_C)
            P_water_kPa = conditions.relative_humidity * P_sat_kPa
            # Adjust pressure for water vapor
            P_dry_kPa = pressure_abs_kPa - P_water_kPa
        else:
            # Use total pressure when ignoring humidity
            P_dry_kPa = pressure_abs_kPa
            P_water_kPa = 0
    
        # Calculate mass using measured conditions
        mass = (P_dry_kPa * volume_m3) / (R * temp_K)
        
        return mass
    