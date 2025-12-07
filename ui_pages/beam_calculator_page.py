from nicegui import ui
from calculators.beam_calculator import *
from calculators.unit_conversion import second_moment_of_area_units, density_units, stress_units, length_units, force_units, distributed_force_units, torque_units, area_units

class BeamCalculatorPage:
    def __init__(self):
        self.is_updating = False
        self.results = {
        'fixtures': [],
        'loads_moments': [],
        'unknowns': None,
        'important_locations': None,
        'beam_x_values': None,
        'y_force_plot': None,
        'y_shear_plot': None,
        'y_moment_plot': None,
        'y_angle_plot': None,
        'y_deflection_plot': None,
        'max_deflection': 0.0,
        'max_deflection_pos': 0.0,

    }
        self.fixtures = []
        self.distr_load_rows = []
        self.build_ui()


    def build_ui(self):
        #ui.label('Beam Calculator').classes('text-lg mt-6')
        with ui.expansion(text="Calculator Information"):
            ui.restructured_text('''
                                This beam calculator uses Singularity Functions and Euler-Bernoulli Beam Theory to calculate beam deflections.
                                    
                                It is not very accurate for small L/D ratios. It was also made by an idiot so use at your own risk.
                                 
                                It is calculated analytically, not with the finite element method.
                                    
                                The "0" position along the beam is always the left-hand side. All beam position values must be positive.
                                
                                For force inputs, positive is up and negative is down. Gravity points downwards.
                                
                                For moment inputs, counterclockwise is positive.
                                 
                                Material Properties marked (Optional) only affect beam stress and weight calculations, not deflections.
                                ''')
        
        ui.separator()
        ui.label('Inputs and Beam Setup').classes('text-lg mt-6 font-bold')
        with ui.card().classes('w-80'):
            ui.label('Beam Inputs').classes('text-md font-italic')
            with ui.row():
                self.beam_length = ui.number(label='Beam Length', value=48, min=0.0)
                self.beam_length_unit = ui.select(options=length_units, value='in')
            with ui.row():
                self.second_moment_area = ui.number(label='Second Moment of Area', value=0.55176, min=0.0)
                self.second_moment_area_unit = ui.select(options=second_moment_of_area_units, value='in⁴')
            with ui.row():
                self.cross_section_area = ui.number(label="(Optional) Cross Sectional Area", value=0.9375, min=0.0)
                self.cross_section_area_unit = ui.select(options=area_units, value="in²")
            with ui.row():
                self.section_y = ui.number(label="(Optional) Distance from Neutral Axis", value=1.0, min=0.0)
                self.section_y_unit = ui.select(options=length_units, value="in")
        with ui.card().classes('w-80'):
            ui.label('Material Inputs').classes('text-md')
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

        ui.label('Beam Fixture and Load Setup').classes('text-lg mt-6 font-bold')

        with ui.card().classes('w-210'):
            ui.label('Beam Fixtures').classes('text-md')
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

        with ui.card().classes('w-210'):
            ui.label('Beam Point Loads and Moments').classes('text-md')
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
        with ui.card().classes('w-210'):
            ui.label('Beam Distributed Loads').classes('text-md')
            self.distributed_loads_table = ui.column().classes('gap-2')
            
            with self.distributed_loads_table:
                # Header row
                with ui.row().classes('items-center gap-2 text-xs'):
                    ui.label('Start Position').style('width: 120px')
                    ui.label('End Position').style('width: 120px')
                    ui.label('Position Unit').style('width: 120px')
                    ui.label('Load Start Value').style('width: 120px')
                    ui.label('Load End Value').style('width: 120px')
                    ui.label('Load Unit').style('width: 120px')
                    ui.label('').style('width: 40px')
                
                # Container for data rows
                self.distr_loads_rows_container = ui.column().classes('gap-2')
                
                
                # Add row buttons
                with ui.row():
                    ui.button('Add Row', icon='add', on_click=lambda: self.add_load_row('Distributed')).props('flat color=grey-8')
                    ui.button('Add Weight of Beam', icon='add', on_click=self.add_gravity_force).props('flat color=grey-8')

        ui.separator()
        ui.label('')
        ui.button("Solve Beam", on_click=self.solve_beam_button)
        ui.separator()
        
        ui.label('Beam Results').classes('text-lg mt-6 font-bold')
        self.max_deflection_qty = Q(self.results['max_deflection'], 'm')
        self.max_deflection_qty = self.max_deflection_qty.to('mm')
        self.max_deflection_pos_qty = Q(self.results['max_deflection_pos'], 'm')
        self.max_bending_stress_qty = Q(0, 'MPa')
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
        with ui.row().classes('items-center gap-2'):
            ui.label('Max Bending Stress = ')
            self.max_bending_stress_label = ui.label(f"{self.max_bending_stress_qty.magnitude:.6f}")
            ui.button(icon='content_copy', on_click=self.copy_result).props('flat dense round size=sm').classes('bg-white text-black')
            self.max_bending_stress_unit = ui.select(options=stress_units, value='MPa', on_change=self.bending_stress_unit_changed)
        
        
        
        with ui.row().classes('items-center gap-2'):
            self.plot_length_unit = ui.select(options=length_units, value='m', on_change=self.plot_unit_change, label="Plot Length Unit").classes('w-32')
            self.plot_force_unit = ui.select(options=force_units, value='N', on_change=self.plot_unit_change, label="Plot Force Unit").classes('w-32')
        self.beam_plot = ui.plotly(generate_beam_plot(self.results)).classes('w-full')
            
    def convert_plot_units(self, new_length_unit:str, new_force_unit:str):
        converted_results = self.results
        old_length_unit = self.results['length_unit']
        old_force_unit = self.results['force_unit']
        try:
            length_conversion = 1*u(old_length_unit).to(new_length_unit).magnitude
            old_force_per_length_unit = f"{old_force_unit} / {old_length_unit}"
            new_force_per_length_unit = f"{new_force_unit} / {new_length_unit}"
            force_per_length_conversion = 1*u(old_force_per_length_unit).to(new_force_per_length_unit).magnitude
            force_conversion = 1*u(old_force_unit).to(new_force_unit).magnitude
            old_torque_unit = f"{old_force_unit} * {old_length_unit}"
            new_torque_unit = f"{new_force_unit} * {new_length_unit}"
            moment_conversion = 1*u(old_torque_unit).to(new_torque_unit).magnitude
        except:
            ui.notify("Could not convert plot units.")
            return self.results, 'm', 'N'

        converted_results['beam_x_values'] = [x * length_conversion for x in converted_results['beam_x_values']]
        converted_results['y_force_plot'] = [f * force_per_length_conversion for f in converted_results['y_force_plot']]
        converted_results['y_shear_plot'] = [s * force_conversion for s in converted_results['y_shear_plot']]
        converted_results['y_moment_plot'] = [m * moment_conversion for m in converted_results['y_moment_plot']]
        converted_results['y_deflection_plot'] = [d * length_conversion for d in converted_results['y_deflection_plot']]
        converted_results['max_deflection'] = converted_results['max_deflection'] * length_conversion
        converted_results['max_deflection_pos'] = converted_results['max_deflection_pos'] * length_conversion
        #for fixture in converted_results['fixtures']:
        #    fixture[1] = fixture[1] * length_conversion
        for load in converted_results['loads_moments']:
            load[1] = load[1] * length_conversion
            if load[0] == 'Constant Distributed Load' or load[0] == 'Linear Distributed Load':
                load[2] = load[2] * length_conversion
            load[3] = load[3] * length_conversion
        for reaction in converted_results['reactions']:
            print(reaction)
            if reaction[0] > 2:
                reaction[2] = reaction[2] * length_conversion
                if reaction[1] == 'Moment':
                    reaction[3] = reaction[3] * moment_conversion
                elif reaction[1] == 'Force y':
                    reaction[3] = reaction[3] * force_conversion
            elif (reaction[0] == 1):
                reaction[3] = reaction[3] * length_conversion # the second integration constant has length units
        for loc in converted_results['important_locations']:
            loc[1] = loc[1] * length_conversion
        print(converted_results)
        self.results['length_unit'] = new_length_unit
        self.results['force_unit'] = new_force_unit
        return converted_results, new_length_unit, new_force_unit
    
    def plot_unit_change(self):
        # convert results values to new units
        # refresh plots
        converted_results, out_length_unit, out_force_unit= self.convert_plot_units(self.plot_length_unit.value, self.plot_force_unit.value)
        self.beam_plot.figure = generate_beam_plot(converted_results, out_length_unit, out_force_unit)
        self.beam_plot.update()
        ui.notify("Beam Results Updated.")
        return
    
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
                return

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
                
            except:
                ui.notify('Error: Check Beam Distributed Load Data.')
                return
        return data
    
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
            except:
                ui.notify('Error: Check Beam Point Load Data.')
                return
        return data
         
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
    
    def solve_beam_button(self):
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
        self.fixtures = []
        for fixture in fixture_dict_list:
            fixture_pos_m = fixture['qty'].to('m')
            if fixture['qty'] > beam_length_qty:
                ui.notify('Fixture position not on beam. Did not solve beam.')
                return
            self.fixtures.append([fixture['type'], fixture_pos_m.magnitude])
        
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
        self.results = solve_beam(loads_moments, self.fixtures, beam_length_qty.magnitude, second_moment_area_qty.magnitude, modulus_elasticity_qty.magnitude, 10, 'm', 'N')
        
        self.max_deflection_qty = Q(self.results['max_deflection'], 'm')
        self.max_deflection_qty = self.max_deflection_qty.to('mm')
        self.max_deflection_pos_qty = Q(self.results['max_deflection_pos'], 'm')
        max_moment_qty = Q(max(self.results['y_moment_plot']), 'N * m')
        second_moment_qty = Q(self.second_moment_area.value, self.second_moment_area_unit.value)
        section_y_qty = Q(self.section_y.value, self.section_y_unit.value)
        self.max_bending_stress_qty = max_moment_qty * section_y_qty / second_moment_qty
        self.max_bending_stress_qty = self.max_bending_stress_qty.to('MPa')
        self.max_deflection_label.text = f"{self.max_deflection_qty.magnitude:.4f}"
        self.max_deflection_pos_label.text = f"{self.max_deflection_pos_qty.magnitude:.6f}"
        self.max_deflection_unit.value = f"{self.max_deflection_qty.units:~P}"
        self.max_deflection_pos_unit.value = f"{self.max_deflection_pos_qty.units:~P}"
        self.max_bending_stress_label.text = f"{self.max_bending_stress_qty.magnitude:.4f}"
        self.max_bending_stress_unit.value = f"{self.max_bending_stress_qty.units:~P}"

        # Update each plotly component by assigning a new figure
        self.plot_length_unit.value = 'm'
        self.plot_force_unit.value = 'N'
        self.beam_plot.figure = generate_beam_plot(self.results)
        self.beam_plot.update()
        ui.notify("Beam Results Updated.")
        
    def deflection_unit_changed(self):
        self.max_deflection_qty = self.max_deflection_qty.to(self.max_deflection_unit.value)
        self.max_deflection_label.text = f"{self.max_deflection_qty.magnitude:.4f}"
        ui.notify("updated deflection")
    
    def deflection_pos_unit_changed(self):
        self.max_deflection_pos_qty = self.max_deflection_pos_qty.to(self.max_deflection_pos_unit.value)
        self.max_deflection_pos_label.text = f"{self.max_deflection_pos_qty.magnitude:.4f}"
    
    def bending_stress_unit_changed(self):
        self.max_bending_stress_qty = self.max_bending_stress_qty.to(self.max_bending_stress_unit.value)
        self.max_bending_stress_label.text = f"{self.max_bending_stress_qty.magnitude:.4f}"
    
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