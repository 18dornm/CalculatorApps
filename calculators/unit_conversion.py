from pint import UnitRegistry

u = UnitRegistry()

def convert(value: float, from_unit:str, to_unit:str):
    '''Convert value between units using Pint.'''
    try:
        quantity = value * u(from_unit)
        return quantity.to(to_unit).magnitude
    except Exception:
        return None
    
'''
# testing:
# length miles to cm
print(convert(12.3, "mile", "cm"))
# mass g to slug
print(convert(12.3, "gram", "slug"))
# torque lbf-in to nm
print(convert(12.3, "lbf * inch", "kgf * cm"))
'''




