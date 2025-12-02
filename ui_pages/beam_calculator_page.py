from nicegui import ui
from calculators.beam_calculator import *
from calculators.unit_conversion import second_moment_of_area_units, density_units, stress_units, length_units, force_units, distributed_force_units, torque_units, area_units

class BeamCalculatorPage:
    def __init__(self):
        self.build_ui()
    
    def build_ui(self):
        with ui.row().classes('items-center gap-2'):
            ui.label('Beam Calculator').classes('text-lg mt-6')
            with ui.icon('o_info').props('flat dense round size=sm').classes('bg-white text-black'):
                ui.tooltip("This beam calculator uses Euler-Bernoulli Beam theory. It isn't very accurate for beams with small L/D ratios.\nIt was also made by an idiot. Use at your own risk.")
        ui.separator()
        ui.label('Inputs and Beam Setup').classes('text-lg mt-6')
        ui.label('Beam Inputs')
        with ui.row():
            self.beam_length = ui.number(label='Beam Length', value=48, min=0.0)
            self.beam_length_unit = ui.select(options=length_units, value='in')
        with ui.row():
            self.second_moment_area = ui.number(label='Second Moment of Area', value=0.55176, min=0.0)
            self.second_moment_area_unit = ui.select(options=second_moment_of_area_units, value='in⁴')
        with ui.row():
            self.cross_section_area = ui.number(label="(Optional) Cross Sectional Area", value=0.9375, min=0.0)
            self.cross_section_area_unit = ui.select(options=area_units, value="in²")

        ui.label('Material Inputs')
        self.material_quickselect = ui.select(label='Material Selection', options=materials, value=materials[0], on_change=self.material_change).classes('w-64')
        with ui.row():
            self.modulus = ui.number(label='Modulus of Elasticity', value=29000, min=0.0, on_change=self.material_prop_change)
            self.modulus_unit = ui.select(options=stress_units, value='ksi', on_change=self.material_prop_change)
        with ui.row():
            self.density = ui.number(label='(Optional) Material Density', value=0.284, min=0.0, on_change=self.material_prop_change)
            self.density_unit = ui.select(options=density_units, value='lb/in³', on_change=self.material_prop_change)
        with ui.row():
            self.yield_strength = ui.number(label='(Optional) Yield Strength', value=36.0, min=0.0, on_change=self.material_prop_change)
            self.yield_strength_unit = ui.select(options=stress_units, value='ksi', on_change=self.material_prop_change)
        ui.separator()

        ui.label('Beam Fixtures').classes('text-lg mt-6')
        self.beam_fixture_table = ui.column().classes('gap-2')
        
        with self.beam_fixture_table:
            # Header row
            with ui.row().classes('items-center gap-2 font-bold'):
                ui.label('Type').style('width: 150px')
                ui.label('Position').style('width: 120px')
                ui.label('Position Unit').style('width: 120px')
                ui.label('').style('width: 40px')
            
            # Container for data rows
            self.fixture_rows_container = ui.column().classes('gap-2')
            self.fixture_rows = []
            
            # Add row button
            ui.button('Add Row', icon='add', on_click=self.add_fixture_row).props('flat color=grey-8')
        ui.separator()

        ui.label('Beam Loads and Moments').classes('text-lg mt-6')
        self.loads_moments_table = ui.column().classes('gap-2')
        
        with self.loads_moments_table:
            # Header row
            with ui.row().classes('items-center gap-2 font-bold'):
                ui.label('Type').style('width: 150px')
                ui.label('Start Position').style('width: 120px')
                ui.label('End Position').style('width: 120px')
                ui.label('Position Unit').style('width: 120px')
                ui.label('Load Start Value').style('width: 120px')
                ui.label('Load End Value').style('width: 120px')
                ui.label('Load Unit').style('width: 120px')
                ui.label('').style('width: 40px')
            
            # Container for data rows
            self.loads_rows_container = ui.column().classes('gap-2')
            self.load_rows = []
            
            # Add row buttons
            with ui.row():
                ui.button('Add Row', icon='add', on_click=self.add_load_row).props('flat color=grey-8')
                ui.button('Add Weight of Beam', icon='add', on_click=self.add_gravity_force).props('flat color=grey-8')
            ui.separator()
            ui.label('')
            ui.button("Solve Beam", on_click=self.solve_beam_button)
            ui.separator()
            ui.label('Beam Results').classes('text-lg mt-6')
        
    def add_fixture_row(self):
        row = BeamFixtureRow(self.fixture_rows_container, page=self)
        self.fixture_rows.append(row)
    
    def get_fixture_data(self):
        data = []
        for row in self.fixture_rows:
            data.append({
                'type': row.type_select.value,
                'qty': Q(row.position_input.value, row.unit_select.value)
            })
        return data
    
    def add_load_row(self):
        row = LoadMomentRow(self.loads_rows_container, page=self)
        self.load_rows.append(row)
    
    def add_gravity_force(self):
        gravity_load = beam_weight_per_length(self.cross_section_area.value, self.cross_section_area_unit.value,
                                   self.density.value, self.density_unit.value)
        gravity_load = gravity_load.to('N/m')
        row = LoadMomentRow(self.loads_rows_container,
                     type_val="Distributed Load", start_pos=0, end_pos=self.beam_length.value, pos_unit='m',
                     start_val=round(gravity_load.magnitude,4), end_val=round(gravity_load.magnitude,4), load_unit='N/m',
                     page=self)
        self.load_rows.append(row)

    def get_load_data(self):
        data = []
        for row in self.load_rows:
            data.append({
                'type': row.type_select.value,
                'start_position_qty': Q(row.start_position.value, row.position_unit.value),
                'end_position_qty': Q(row.end_position.value, row.position_unit.value),
                'load_start_qty': Q(row.load_start_value.value, row.load_unit.value),
                'load_end_qty': Q(row.load_end_value.value, row.load_unit.value)
            })
        
    def material_change(self):
        #TODO: update material modulus, density, yield strength based on selection.
        return 0
    
    def material_prop_change(self):
        #TODO: change value of material_quickselect to 'Custom'
        self.material_quickselect.value = 'Custom'
        return 0
    
    def solve_beam_button(self):
        #TODO: checks for if inputs are correct, then converts units to be consistent, then solves beam, then updates plots
        # get all the values
        beam_length_qty = Q(self.beam_length.value, self.beam_length_unit.value)
        beam_length_qty = beam_length_qty.to('m')
        second_moment_area_qty = Q(self.second_moment_area.value, self.second_moment_area_unit.value)
        second_moment_area_qty = second_moment_area_qty.to('m**4')
        modulus_elasticity_qty = Q(self.modulus.value, self.modulus_unit.value)
        modulus_elasticity_qty = modulus_elasticity_qty.to('Pa')
        # Check if inputs are correct (fixture position inside bounds)
        fixtures = self.get_fixture_data()
        for fixture in fixtures:
            if fixture['qty'] > beam_length_qty:
                ui.notify('Fixture not on Beam. Did not solve beam.')
                return
        loads = self.get_load_data()
        for load in loads:
            if load['start_position_qty'] > beam_length_qty:
                ui.notify('Start position not on beam. Did not solve beam.')
                return
            if load['end_position_qty'] > beam_length_qty:
                ui.notify('End position not on beam. Did not solve beam.')
                return
            if load['type'] == 'Distributed Load':
                # check that none of them are empty
                if load['start_position_qty'] > load['end_position_qty']:
                    ui.notify('Distributed Load start position must come after end position. Did not solve beam.')
                    return
                if ((load['load_start_value'] < 0 and load['load_end_value'] > 0) or (load['load_end_value'] < 0 and load['load_start_value'] > 0)):
                    ui.notify('Distributed loads cannot have both positive and negative values. Did not solve beam.')
                    return



        return 0

class BeamFixtureRow:
    def __init__(self, table_container, page=None):
        self.table_container = table_container
        self.page = page
        with table_container:
            self.row_container = ui.row().classes('items-center gap-2')
            with self.row_container:
                self.type_select = ui.select(options=fixture_types).style('width: 150px')
                self.position_input = ui.number(min=0.0).style('width: 120px')
                self.unit_select = ui.select(options=length_units).style('width: 120px')
                ui.button(icon='close', on_click=self.delete).props('flat dense')
    
    def delete(self):
        self.table_container.remove(self.row_container)
        self.page.fixture_rows.remove(self)

class LoadMomentRow:
    def __init__(self, table_container,
                 type_val=None, start_pos=None, end_pos=None, pos_unit=None,
                 start_val=None, end_val=None, load_unit=None, page=None):
        self.table_container = table_container
        self.page = page
        with table_container:
            self.row_container = ui.row().classes('items-center gap-2')
            with self.row_container:
                self.type_select = ui.select(
                    options=load_moment_types,
                    value=type_val,
                    on_change=self.update_load_unit_options
                ).style('width: 150px')
                
                self.start_position = ui.number(value=start_pos, min=0.0).style('width: 120px')
                self.end_position = ui.number(value=end_pos, min=0.0).style('width: 120px')
                self.position_unit = ui.select(options=length_units, value=pos_unit).style('width: 120px')
                self.load_start_value = ui.number(value=start_val).style('width: 120px')
                self.load_end_value = ui.number(value=end_val).style('width: 120px')
                self.load_unit = ui.select(options=[]).style('width: 120px')
                
                ui.button(icon='close', on_click=self.delete).props('flat dense')
        
        # Initialize load unit options
        self.update_load_unit_options()
        if load_unit is not None:
            self.load_unit.value = load_unit
    
    def update_load_unit_options(self):
        type_val = self.type_select.value
        if type_val == "Concentrated Force":
            self.load_unit.options = force_units
        elif type_val == "Concentrated Moment":
            self.load_unit.options = torque_units
        elif type_val == "Distributed Load":
            self.load_unit.options = distributed_force_units
        else:
            self.load_unit.options = []
        self.load_unit.update()
    
    def delete(self):
        self.table_container.remove(self.row_container)
        if self.page:
            self.page.load_rows.remove(self)