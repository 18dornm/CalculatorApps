from nicegui import ui
from calculators.beam_calculator import *
from calculators.unit_conversion import second_moment_of_area_units, density_units, stress_units, length_units, force_units, distributed_force_units, torque_units, area_units

class BeamCalculatorPage:
    def __init__(self):
        self.is_updating = False
        self.results = {
        'unknowns': None,
        'important_locations': None,
        'beam_x_values': None,
        'y_force_plot': None,
        'y_shear_plot': None,
        'y_moment_plot': None,
        'y_angle_plot': None,
        'y_deflection_plot': None,
        'max_deflection': 0.0,
        'max_deflection_pos': 0.0
    }
        self.build_ui()


    def build_ui(self):
        with ui.row().classes('items-center gap-2'):
            ui.label('Beam Calculator').classes('text-lg mt-6')
            with ui.icon('o_info').props('flat dense round size=sm').classes('bg-white text-black'):
                ui.tooltip("This beam calculator uses Euler-Bernoulli Beam theory. It isn't very accurate for beams with small L/D ratios.\nIt was also made by an idiot. Use at your own risk.")
        ui.separator()
        ui.label('Inputs and Beam Setup').classes('text-lg mt-6')
        ui.label('Beam Inputs').classes('text-md font-bold')
        with ui.row():
            self.beam_length = ui.number(label='Beam Length', value=48, min=0.0)
            self.beam_length_unit = ui.select(options=length_units, value='in')
        with ui.row():
            self.second_moment_area = ui.number(label='Second Moment of Area', value=0.55176, min=0.0)
            self.second_moment_area_unit = ui.select(options=second_moment_of_area_units, value='in⁴')
        with ui.row():
            self.cross_section_area = ui.number(label="(Optional) Cross Sectional Area", value=0.9375, min=0.0)
            self.cross_section_area_unit = ui.select(options=area_units, value="in²")

        ui.label('Material Inputs').classes('text-md font-bold')
        self.material_quickselect = ui.select(label='Material Selection', options=materials_list, value='Custom', on_change=self.material_change).classes('w-64')
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

        ui.label('Beam Fixture and Load Setup').classes('text-lg mt-6')
        ui.label('Beam Fixtures').classes('text-md font-bold')
        self.beam_fixture_table = ui.column().classes('gap-2')
        
        with self.beam_fixture_table:
            # Header row
            with ui.row().classes('items-center gap-2'):
                ui.label('Type').style('width: 150px')
                ui.label('Position').style('width: 120px')
                ui.label('Position Unit').style('width: 120px')
                ui.label('').style('width: 40px')
            
            # Container for data rows
            self.fixture_rows_container = ui.column().classes('gap-2')
            self.fixture_rows = []
            
            # Add row button
            ui.button('Add Row', icon='add', on_click=self.add_fixture_row).props('flat color=grey-8')
        #ui.separator()

        ui.label('Beam Point Loads and Moments').classes('text-md font-bold')
        self.point_loads_table = ui.column().classes('gap-2')
        with self.point_loads_table:
            # Header row
            with ui.row().classes('items-center gap-2'):
                ui.label('Type').style('width: 150px')
                ui.label('Position').style('width: 120px')
                ui.label('Position Unit').style('width: 120px')
                ui.label('Load Value').style('width: 120px')
                ui.label('Load Unit').style('width: 120px')
                ui.label('').style('width: 40px')
            
            # Container for data rows
            self.loads_rows_container = ui.column().classes('gap-2')
            self.load_rows = []
            
            # Add row buttons
            ui.button('Add Row', icon='add', on_click=lambda: self.add_load_row('Point')).props('flat color=grey-8')

        #ui.separator()

        ui.label('Beam Distributed Loads').classes('text-md font-bold')
        self.distributed_loads_table = ui.column().classes('gap-2')
        
        with self.distributed_loads_table:
            # Header row
            with ui.row().classes('items-center gap-2 font-bold'):
                ui.label('Start Position').style('width: 120px')
                ui.label('End Position').style('width: 120px')
                ui.label('Position Unit').style('width: 120px')
                ui.label('Load Start Value').style('width: 120px')
                ui.label('Load End Value').style('width: 120px')
                ui.label('Load Unit').style('width: 120px')
                ui.label('').style('width: 40px')
            
            # Container for data rows
            self.distr_loads_rows_container = ui.column().classes('gap-2')
            self.distr_load_rows = []
            
            # Add row buttons
            with ui.row():
                ui.button('Add Row', icon='add', on_click=lambda: self.add_load_row('Distributed')).props('flat color=grey-8')
                ui.button('Add Weight of Beam', icon='add', on_click=self.add_gravity_force).props('flat color=grey-8')
            ui.separator()
            ui.label('')
            ui.button("Solve Beam", on_click=self.solve_beam_button)
            ui.separator()
            ui.label('Beam Results').classes('text-lg mt-6')
            self.max_deflection_qty = Q(self.results['max_deflection'], 'm')
            self.max_deflection_qty = self.max_deflection_qty.to('mm')
            self.max_deflection_pos_qty = Q(self.results['max_deflection_pos'], 'm')
            with ui.row().classes('items-center gap-2'):
                    ui.label('Max Deflection = ')
                    self.max_deflection_label = ui.label(f"{self.max_deflection_qty.magnitude:.4f}")
                    ui.button(icon='content_copy', on_click=self.copy_result).props('flat dense round size=sm').classes('bg-white text-black')
                    self.max_deflection_unit = ui.select(options=length_units, value='mm', on_change=self.deflection_unit_changed)
            with ui.row().classes('items-center gap-2'):
                    ui.label('Location of Max Deflection = ')
                    self.max_deflection_pos_label = ui.label(f"{self.max_deflection_pos_qty.magnitude:.6f}")
                    ui.button(icon='content_copy', on_click=self.copy_result).props('flat dense round size=sm').classes('bg-white text-black')
                    self.max_deflection_pos_unit = ui.select(options=length_units, value='m', on_change=self.deflection_pos_unit_changed)
            ui.label('Beam Setup Plot').classes('text-lg mt-6')
            self.load_plot = ui.plotly(generate_load_diagram(self.results)).classes('w-full')
            ui.label('Shear and Moment Diagrams')
            self.shear_moment_plot = ui.plotly(generate_shear_moment_diagram(self.results)).classes('w-full')
            ui.label('Deflection and Angle Diagram')
            self.deflection_plot = ui.plotly(generate_deflection_diagram(self.results)).classes('w-full')
            
        
    def add_fixture_row(self):
        row = BeamFixtureRow(self.fixture_rows_container, page=self)
        self.fixture_rows.append(row)
    
    def get_fixture_data(self):
        data = []
        for row in self.fixture_rows:
            try:
                data.append({
                    'type': row.type_select.value,
                    'qty': Q(row.position_input.value, row.unit_select.value)
                })
            except:
                ui.notify('Error: Check Beam Fixture Data.')

        return data
    
    def add_load_row(self, load_type):
        if load_type == 'Distributed':
            row = DistributedLoadRow(self.distr_loads_rows_container, page=self)
            self.distr_load_rows.append(row)
        else:
            row = PointLoadRow(self.loads_rows_container, page=self)
            self.load_rows.append(row)
    
    def add_gravity_force(self):
        gravity_load = beam_weight_per_length(self.cross_section_area.value, self.cross_section_area_unit.value,
                                   self.density.value, self.density_unit.value)
        gravity_load = gravity_load.to('N/m')
        row = DistributedLoadRow(self.distr_loads_rows_container,
                                 start_pos=0, end_pos=self.beam_length.value, pos_unit=self.beam_length_unit.value,
                                 start_val=round(gravity_load.magnitude,4), end_val=round(gravity_load.magnitude,4), load_unit='N/m',
                                 page=self)
        self.distr_load_rows.append(row)

    def get_distr_load_data(self):
        data = []
        for row in self.distr_load_rows:
            try:
                data.append({
                    'type': 'Distributed Load',
                    'start_position_qty': Q(row.start_position.value, row.position_unit.value),
                    'end_position_qty': Q(row.end_position.value, row.position_unit.value),
                    'load_start_qty': Q(row.load_start_value.value, row.load_unit.value),
                    'load_end_qty': Q(row.load_end_value.value, row.load_unit.value)
                })
                return data
            except:
                ui.notify('Error: Check Beam Distributed Load Data.')
    
    def get_point_load_data(self):
        data = []
        for row in self.load_rows:
            try:
                data.append({
                    'type': row.type_select.value,
                    'start_position_qty': Q(row.position.value, row.position_unit.value),
                    'end_position_qty': None,
                    'load_start_qty': Q(row.load_value.value, row.load_unit.value),
                    'load_end_qty': None
                })
                return data
            except:
                ui.notify('Error: Check Beam Point Load Data.')
         
    def material_change(self):
        self.is_updating = True
        if self.material_quickselect.value == 'Custom':
            return
        selected_material = materials.get(self.material_quickselect.value)
        self.modulus.value = selected_material.modulus.magnitude
        self.modulus_unit.value = f"{selected_material.modulus.units:~P}"
        self.density.value = selected_material.density.magnitude
        self.density_unit.value = f"{selected_material.density.units:~P}"
        self.yield_strength.value = selected_material.yield_strength.magnitude
        self.yield_strength_unit.value = f"{selected_material.yield_strength.units:~P}"
        self.is_updating = False
    
    def material_prop_change(self):
        if not self.is_updating:
            self.material_quickselect.value = 'Custom'
    
    async def solve_beam_button(self):
        # get all the values
        try:
            beam_length_qty = Q(self.beam_length.value, self.beam_length_unit.value)
            beam_length_qty = beam_length_qty.to('m')
            second_moment_area_qty = Q(self.second_moment_area.value, self.second_moment_area_unit.value)
            second_moment_area_qty = second_moment_area_qty.to('m**4')
            modulus_elasticity_qty = Q(self.modulus.value, self.modulus_unit.value)
            modulus_elasticity_qty = modulus_elasticity_qty.to('Pa')
        except:
            ui.notify('Error: Check Beam Setup Data.')
            return
        # Check if inputs are correct (fixture position inside bounds)
        fixture_dict_list = self.get_fixture_data()
        fixtures = []
        for fixture in fixture_dict_list:
            fixture_pos_m = fixture['qty'].to('m')
            if fixture['qty'] > beam_length_qty:
                ui.notify('Fixture position not on beam. Did not solve beam.')
                return
            fixtures.append([fixture['type'], fixture_pos_m.magnitude])
        
        loads_moments = []
        distr_loads = self.get_distr_load_data()
        if distr_loads != None:
            for load in distr_loads:
                load_start_pos = load['start_position_qty'].to('m')
                load_end_pos = load['end_position_qty'].to('m')
                load_start = load['load_start_qty'].to('N/m')
                load_end = load['load_end_qty'].to('N/m')
                if load_start_pos > beam_length_qty:
                    ui.notify('Start position not on beam. Did not solve beam.')
                    return
                if load_end_pos > beam_length_qty:
                    ui.notify('End position not on beam. Did not solve beam.')
                    return
                if load_start_pos > load_end_pos:
                    ui.notify('Distributed Load start position must come after end position. Did not solve beam.')
                    return
                if ((load_start < 0 and load_end > 0) or (load_end < 0 and load_start > 0)):
                    ui.notify('Distributed loads cannot have both positive and negative values. Split it into two loads. Did not solve beam.')
                    return
                if (load_start == load_end):
                    loads_moments.append(['Constant Distributed Load', load_start_pos.magnitude, load_end_pos.magnitude, load_start.magnitude])
                elif ((load_start > load_end) and (load_start.magnitude < 0) and (load_end.magnitude < 0)):
                    # common way to treat all other linear loads (constant distr + linear distr starting from 0)
                    # load ramps downward and is negative. This one requires the max to get the signs right
                    const_load = max(load_start, load_end)
                    lin_load = load_end - load_start
                    loads_moments.append(['Constant Distributed Load', load_start_pos.magnitude, load_end_pos.magnitude, const_load.magnitude])
                    loads_moments.append(['Linear Distributed Load', load_start_pos.magnitude, load_end_pos.magnitude, lin_load.magnitude])
                else: 
                    # common way to treat all other linear loads (constant distr + linear distr starting from 0)
                    const_load = min(load_start, load_end)
                    lin_load = load_end - load_start
                    loads_moments.append(['Constant Distributed Load', load_start_pos.magnitude, load_end_pos.magnitude, const_load.magnitude])
                    loads_moments.append(['Linear Distributed Load', load_start_pos.magnitude, load_end_pos.magnitude, lin_load.magnitude])
                
        point_loads = self.get_point_load_data()
        if point_loads != None:
            for load in point_loads:
                if load['type'] == 'Concentrated Force':
                    load_val = load['load_start_qty'].to('N')
                    load_pos = load['start_position_qty'].to('m')
                    if load_pos > beam_length_qty:
                        ui.notify('Point load position not on beam. Did not solve beam.')
                        return
                    loads_moments.append([load['type'], load_pos.magnitude, None, load_val.magnitude])
                if load['type'] == 'Concentrated Moment':
                    load_val = load['load_start_qty'].to('N*m')
                    load_pos = load['start_position_qty'].to('m')
                    if load_pos > beam_length_qty:
                        ui.notify('Point load position not on beam. Did not solve beam.')
                        return
                    loads_moments.append([load['type'], load_pos.magnitude, None, load_val.magnitude])
        
        # now solve the beam (eventually put this in a try except)
        self.results = solve_beam(loads_moments, fixtures, beam_length_qty.magnitude, second_moment_area_qty.magnitude, modulus_elasticity_qty.magnitude, num_points=250)
        
        self.max_deflection_qty = Q(self.results['max_deflection'], 'm')
        self.max_deflection_qty = self.max_deflection_qty.to('mm')
        self.max_deflection_pos_qty = Q(self.results['max_deflection_pos'], 'm')
        self.max_deflection_label.text = f"{self.max_deflection_qty.magnitude:.4f}"
        self.max_deflection_pos_label.text = f"{self.max_deflection_pos_qty.magnitude:.6f}"
        self.max_deflection_unit.value = f"{self.max_deflection_qty.units:~P}"
        self.max_deflection_pos_unit.value = f"{self.max_deflection_pos_qty.units:~P}"
        # Update each plotly component by assigning a new figure
        self.load_plot.figure = generate_load_diagram(self.results)
        self.shear_moment_plot.figure = generate_shear_moment_diagram(self.results)
        self.deflection_plot.figure = generate_deflection_diagram(self.results)

        # Optionally trigger redraw if needed:
        self.load_plot.update()
        self.shear_moment_plot.update()
        self.deflection_plot.update()
        ui.notify("Beam Results Updated.")


    def update_results_section(self):
        self.max_deflection_qty = Q(self.results['max_deflection'], 'm')
        self.max_deflection_qty = self.max_deflection_qty.to('mm')
        self.max_deflection_pos_qty = Q(self.results['max_deflection_pos'], 'm')
        self.max_deflection_label.text = f"{self.max_deflection_qty.magnitude:.4f}"
        self.max_deflection_pos_label.text = f"{self.max_deflection_pos_qty.magnitude:.6f}"
        self.max_deflection_unit.value = f"{self.max_deflection_qty.units:~P}"
        self.max_deflection_pos_unit.value = f"{self.max_deflection_pos_qty.units:~P}"
        

        
    
    def deflection_unit_changed(self):
        self.max_deflection_qty = self.max_deflection_qty.to(self.max_deflection_unit.value)
        self.max_deflection_label.text = f"{self.max_deflection_qty.magnitude:.4f}"
        ui.notify("updated deflection")
    
    def deflection_pos_unit_changed(self):
        self.max_deflection_pos_qty = self.max_deflection_pos_qty.to(self.max_deflection_pos_unit.value)
        self.max_deflection_pos_label.text = f"{self.max_deflection_pos_qty.magnitude:.4f}"
        ui.notify("updated position of deflection")
    
    def copy_result(self):
        ui.run_javascript(f'navigator.clipboard.writeText("{self.volume_output.text}");')
        ui.notify('Copied to Clipboard', timeout=1)

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

class DistributedLoadRow:
    def __init__(self, table_container,
                 type_val=None, start_pos=None, end_pos=None, pos_unit=None,
                 start_val=None, end_val=None, load_unit=None, page=None):
        self.table_container = table_container
        self.page = page
        with table_container:
            self.row_container = ui.row().classes('items-center gap-2')
            with self.row_container:
                
                self.start_position = ui.number(value=start_pos, min=0.0).style('width: 120px')
                self.end_position = ui.number(value=end_pos, min=0.0).style('width: 120px')
                self.position_unit = ui.select(options=length_units, value=pos_unit).style('width: 120px')
                self.load_start_value = ui.number(value=start_val).style('width: 120px')
                self.load_end_value = ui.number(value=end_val).style('width: 120px')
                self.load_unit = ui.select(options=distributed_force_units).style('width: 120px')
                
                ui.button(icon='close', on_click=self.delete).props('flat dense')
        
        # Initialize load unit options
        if load_unit is not None:
            self.load_unit.value = load_unit
    
    def delete(self):
        self.table_container.remove(self.row_container)
        if self.page:
            self.page.distr_load_rows.remove(self)

class PointLoadRow:
    def __init__(self, table_container,
                 type_val=None, pos=None, pos_unit=None,
                 load=None, load_units=None, page=None):
        self.table_container = table_container
        self.page = page
        with table_container:
            self.row_container = ui.row().classes('items-center gap-2')
            with self.row_container:
                self.type_select = ui.select(
                    options=['Concentrated Force', 'Concentrated Moment'],
                    value=type_val,
                    on_change=self.update_load_unit_options
                ).style('width: 180px')
                
                self.position = ui.number(value=pos, min=0.0).style('width: 120px')
                self.position_unit = ui.select(options=length_units, value=pos_unit).style('width: 120px')
                self.load_value = ui.number(value=load).style('width: 120px')
                self.load_unit = ui.select(options=[]).style('width: 120px')
                
                ui.button(icon='close', on_click=self.delete).props('flat dense')
        
        # Initialize load unit options
        self.update_load_unit_options()
        if load_units is not None:
            self.load_unit.value = load_units
    
    def update_load_unit_options(self):
        type_val = self.type_select.value
        if type_val == "Concentrated Force":
            self.load_unit.options = force_units
        elif type_val == "Concentrated Moment":
            self.load_unit.options = torque_units
        else:
            self.load_unit.options = []
        self.load_unit.update()
    
    def delete(self):
        self.table_container.remove(self.row_container)
        if self.page:
            self.page.load_rows.remove(self)