from pint import UnitRegistry
ureg = UnitRegistry()
#all_units = list(ureg._units.keys())
#print(sorted(all_units))

torque_compatible = ureg.get_compatible_units('meter')
torque_units = [str(unit) for unit in torque_compatible]
print(torque_units)

#torque1 = 12 * u.('N*m')
Q_ = ureg.Quantity
volume = Q_(1, '°C')
#vol1 = volume.to('liters')
#vol2 = volume.to('cubic meters')
#print(vol2)
#print(vol1)
print(volume)
vol_str = f"{volume.units:~P}"
print(vol_str)
'''
# Get all unit names/aliases, excluding private/magic methods and other attributes
units = [name for name in dir(ureg) if not name.startswith('_')]

# Further filter to only actual units (exclude methods and properties)
units = [name for name in dir(ureg) 
         if not name.startswith('_') 
         and not callable(getattr(ureg, name, None)) 
         or name in ['meter', 'second']]  # callable check might filter some units

# Simpler approach - just filter out common non-unit attributes
non_units = {'default_format', 'force_ndarray_like', 'auto_reduce_dimensions', 
             'autoconvert_offset_to_baseunit', 'case_sensitive', 'Quantity', 
             'Unit', 'Measurement', 'Context', 'Group', 'System'}
units = [name for name in dir(ureg) 
         if not name.startswith('_') and name not in non_units]

print(sorted(units))
'''