from pint import UnitRegistry
u = UnitRegistry()
Q = u.Quantity

fixture_types = ['Fixed', 'Pinned/Roller']
load_moment_types = ['Concentrated Force', 'Distributed Load', 'Concentrated Moment']

def beam_weight_per_length(area:float, area_unit:str, density:float, density_unit:str):
    area_qty = Q(area, area_unit)
    density_qty = Q(density, density_unit)
    return area_qty * density_qty * -1 * u.standard_gravity


class Material:
    def __init__(self, name, modulus, density, yield_strength):
        self.name = name
        self.modulus = modulus
        self.density = density
        self.yield_strength=yield_strength

al_6061_T6 = Material('Aluminum 6061-T6', Q(10000, 'ksi'), Q(0.0975, 'lb/in**3'), Q(40.0, 'ksi'))
al_7075_T6 = Material('Aluminum 7075-T6', Q(10400, 'ksi'), Q(0.102, 'lb/in**3'), Q(73.0, 'ksi'))
al_5052_H32 = Material('Aluminum 5052-H32', Q(10200, 'ksi'), Q(0.0975, 'lb/in**3'), Q(28, 'ksi'))
al_6063_T6 = Material('Aluminum 6063-T6', Q(10000, 'ksi'), Q(0.0975, 'lb/in**3'), Q(31.0, 'ksi'))
st_1020 = Material('AISI 1020 Steel', Q(29000, 'ksi'), Q(0.284, 'lb/in**3'), Q(42.7, 'ksi'))
st_A500_B = Material('ASTM A500 Grade B', Q(29000, 'ksi'), Q(0.284, 'lb/in**3'), Q(46.0, 'ksi'))
st_4130 = Material('AISI 4130 Chromoly Steel', Q(29700, 'ksi'), Q(0.284, 'lb/in**3'), Q(63.1, 'ksi'))
st_4340 = Material('AISI 4340 Chromoly Steel', Q(29700, 'ksi'), Q(0.284, 'lb/in**3'), Q(103000, 'ksi'))
acetal = Material('Delrin/Acetal Homopolymer', Q(450, 'ksi'), Q(0.051, 'lb/in**3'), Q(11.0, 'ksi'))
polycarbonate = Material('Polycarbonate', Q(335, 'ksi'), Q(0.04335, 'lb/in**3'), Q(11.0, 'ksi'))
uhmw = Material('UHMW', Q(100, 'ksi'), Q(0.03360, 'lb/in**3'), Q(21, 'ksi'))
nylon_pa12 = Material('Nylon PA12', Q(261, 'ksi'), Q(0.03649, 'lb/in**3'), Q(6.97, 'ksi'))

materials = ['Custom', al_6061_T6.name, al_7075_T6.name, al_5052_H32.name, al_6063_T6.name, st_1020.name, st_A500_B.name, st_4130.name, st_4340.name, acetal.name, polycarbonate.name, uhmw.name, nylon_pa12.name]
