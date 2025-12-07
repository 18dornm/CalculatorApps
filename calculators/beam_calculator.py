import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
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

materials = {
    al_6061_T6.name: al_6061_T6,
    al_7075_T6.name: al_7075_T6,
    al_5052_H32.name: al_5052_H32,
    al_6063_T6.name: al_6063_T6,
    
    st_1020.name: st_1020,
    st_A500_B.name: st_A500_B,
    st_4130.name: st_4130,
    st_4340.name: st_4340,
    
    acetal.name: acetal,
    polycarbonate.name: polycarbonate,
    uhmw.name: uhmw,
    nylon_pa12.name: nylon_pa12,
}

materials_list = list(materials.keys())
materials_list.append('Custom')


def locations_of_interest(loads_moments, fixtures):
    '''
    

    Parameters
    ----------
    loads_moments : LIST
        LIST OF LOADS AND MOMENTS WITH THEIR LOCATIONS.
    fixtures : LIST
        LIST OF FIXTURES AND THEIR LOCATIONS.

    Returns
    -------
    important_locations : LIST
        COMBINED LIST OF LOADS AND FIXTURES WITH THEIR LOCATIONS.

    '''
    important_locations = []
    for i in range(len(loads_moments)):
        if(loads_moments[i][0] != None):
            important_locations.append(loads_moments[i][0:2])
            if(loads_moments[i][2] != None):
                important_locations.append([loads_moments[i][0],loads_moments[i][2]])
    for i in range(len(fixtures)):
        if(fixtures[i][0] != None):
            important_locations.append(fixtures[i])
    
    important_locations.sort(key=lambda x: x[1])
    
    return important_locations

    
def find_unknowns(fixtures):
    # if fixed, unknowns are Moment, Py, [Px]. Theta=u=0
    # if pinned, unknowns are Py, [Px], Theta. moment=u=0
    # if roller, unknowns are Py, Theta. [Px]=u=moment=0
    unknowns = []
    unknowns.append([1, "a1", None])
    unknowns.append([2, "a2", None])
    identifier = 3
    
    for fixture in fixtures:
        if fixture[0] == "Fixed":
            unknowns.append([identifier, "Moment", fixture[1]])  # add moment
            unknowns.append([identifier + 1, "Force y", fixture[1]])  # add Py
            # unknowns.append([identifier + 2, "Force x", fixture[1]])  # add Px
            identifier += 2
        elif fixture[0] == "Pinned/Roller":
            unknowns.append([identifier, "Force y", fixture[1]])  # add Py
            # unknowns.append([identifier + 2, "Force x", fixture[1]])  # add Px
            identifier += 1
        #elif fixture[0] == "Roller":
        #    unknowns.append([identifier, "Force y", fixture[1]])  # add Py
        #    identifier += 1
    
    return unknowns


def find_coefficients(forces, unknowns, youngs_modulus, moment_of_inertia, overall_length, selection):
    # go through forces and moments and add them to p coefficients.
    # use the singularity function rules to determine exponent. identifier is 1000+ sequential
    # go through unknowns and add them to the p coefficients. Choose the correct singularity function
    # sort the p coefficients by location (L to R)
    identifier = 1000
    n = -1
    p_coeffs = []  # id, coefficient(value), location, exponent
    for force in forces:
        if force[0] == "Concentrated Force":
            n = -1
            p_coeffs.append([identifier, force[3], force[1], n])
            identifier += 1
        elif force[0] == "Concentrated Moment":
            n = -2
            p_coeffs.append([identifier, force[3], force[1], n])
            identifier += 1
        elif force[0] == "Constant Distributed Load":
            n = 0
            p_coeffs.append([identifier, force[3], force[1], n])
            identifier += 1
            if force[2] < overall_length:
                p_coeffs.append([identifier, -1 * force[3], force[2], n])
                identifier += 1
        elif force[0] == "Linear Distributed Load":
            n = 1
            m = force[3] / (force[2] - force[1])
            p_coeffs.append([identifier, m, force[1], n])
            identifier += 1
            if force[2] < overall_length:
                p_coeffs.append([identifier, -1 * m, force[2], n])
                identifier += 1
                p_coeffs.append([identifier, -1 * force[3], force[2], 0])
                identifier += 1
        elif force[0] == "None":
            continue

    for unknown in unknowns:
        if unknown[1] == "Moment":
            n = -2
            p_coeffs.append([unknown[0], 1, unknown[2], n])
        elif unknown[1] == "Force y":
            n = -1
            p_coeffs.append([unknown[0], 1, unknown[2], n])
        else:  # skip a1 and a2 FOR p. add them in as coefficients for theta and u later.
            continue

    v_coeffs = []
    v_coeff = []
    m_coeffs = []
    m_coeff = []
    theta_coeffs = []
    theta_coeff = []
    u_coeffs = []
    u_coeff = []

    # add a1 and a2 to theta and u. Assume a1 and a2 = 1 for now, will solve to find them later.
    theta_coeffs.append([1, 1 / (youngs_modulus * moment_of_inertia), -1, 0])  # want EvalSingularity to return a1
    theta_coeffs.append([2, 0 / (youngs_modulus * moment_of_inertia), 10000000, -1])  # want EvalSingularity to return 0
    u_coeffs.append([1, 1 / (youngs_modulus * moment_of_inertia), 0, 1])  # want EvalSingularity to return a1*x
    u_coeffs.append([2, 1 / (youngs_modulus * moment_of_inertia), -1, 0])  # want EvalSingularity to return a2

    for p_coeff in p_coeffs:
        v_coeff = integrate_singularity(p_coeff)
        v_coeffs.append(v_coeff)
        m_coeff = integrate_singularity(v_coeff)
        m_coeffs.append(m_coeff)
        theta_coeff = integrate_singularity(m_coeff)
        theta_coeff[1] = theta_coeff[1] / (youngs_modulus * moment_of_inertia)
        theta_coeffs.append(theta_coeff)
        u_coeff = integrate_singularity(theta_coeff)
        u_coeffs.append(u_coeff)

    if selection == "P(x) Coefficients":
        return p_coeffs
    if selection == "V(x) Coefficients":
        return v_coeffs
    if selection == "M(x) Coefficients":
        return m_coeffs
    if selection == "Theta(x) Coefficients":
        return theta_coeffs
    if selection == "u(x) Coefficients":
        return u_coeffs


def integrate_singularity(coeffs):
    # coeffs comes in the form [id, coeff, location, exp]
    n = coeffs[3]
    amplitude = coeffs[1]
    if n >= 0:
        amplitude = amplitude / (n + 1)
        n += 1
    if n == -1:
        n = 0
    if n == -2:
        n = -1
    return [coeffs[0], amplitude, coeffs[2], n]


def eval_singularity(coeffs, x):
    # coeffs comes in the form [id, coeff, location, exp]
    amplitude = coeffs[1]
    location = coeffs[2]
    n = coeffs[3]
    if x < location or n < 0:
        return 0
    if x >= location and n == 0:
        return amplitude
    if x >= location and n > 0:
        return amplitude * (x - location) ** n


def create_ab(fixtures, theta_coeffs, u_coeffs, p_coeffs, overall_length, selection):
    b = []
    a = []

    # SUM OF FORCES IN Y DIRECTION
    b.append(0)
    a.append([0, 0])  # first two elements will be 0 for a1 and a2
    for i in range(len(p_coeffs)):
        id_val, mag, loc, exp = p_coeffs[i]
        if id_val < 1000 and exp == -2:  # unknown moment
            a[-1].append(0)  # add 0 to A matrix
        if id_val < 1000 and exp == -1:  # unknown force
            # append F*d directly to A
            a[-1].append(mag)
        if id_val >= 1000 and exp == -2:  # known moment
            # ignore
            b[-1] -= 0
        if id_val >= 1000 and exp == -1:  # known force
            # sum f*d directly to B
            b[-1] -= mag
        if id_val >= 1000 and exp == 0:  # known rect. distr. load
            # sum (w*(Length-loc)) to B
            b[-1] -= (mag * (overall_length - loc))
        if id_val >= 1000 and exp == 1:  # known linear distr. load.
            # sum (w*(1/2)*(Length-Loc)) to B Note that mag is the slope of the line here.
            b[-1] -= (0.5 * mag * (overall_length - loc) ** 2)

    b.append(0)
    a.append([0, 0])  # first two elements will be 0 for a1 and a2

    # SUM OF MOMENTS
    for i in range(len(p_coeffs)):
        id_val, mag, loc, exp = p_coeffs[i]
        if id_val < 1000 and exp == -2:  # unknown moment
            # append directly to A
            a[-1].append(mag)
        elif id_val < 1000 and exp == -1:  # unknown force
            # append F*d directly to A
            a[-1].append(mag * (overall_length - loc))
        elif id_val >= 1000 and exp == -2:  # known moment
            # sum directly to B
            b[-1] -= mag
        elif id_val >= 1000 and exp == -1:  # known force
            # sum f*d directly to B
            b[-1] -= mag * (overall_length - loc)
        elif id_val >= 1000 and exp == 0:  # known rect. distr. load
            # sum (w*(Length-loc))*((Length-loc)/2+loc) to B
            b[-1] -= (mag * (overall_length - loc)) * ((overall_length - loc) / 2)
        elif id_val >= 1000 and exp == 1:  # known linear distr. load
            # sum (w*(1/2)*(Length-Loc))*((2/3)*(Length-loc)) to B
            b[-1] -= (1 / 2) * (overall_length - loc) ** 3 * mag * (1 / 3)

    for i in range(len(fixtures)):
        if fixtures[i][0] == "None":
            continue
        elif fixtures[i][0] == "Fixed":
            b.append(0)
            a.append([])

            x = fixtures[i][1]  # location of fixture
            for j in range(len(u_coeffs)):
                if u_coeffs[j][0] == "":
                    continue
                value_u = eval_singularity(u_coeffs[j], x)
                if u_coeffs[j][0] >= 1000:
                    b[-1] -= value_u
                elif u_coeffs[j][0] < 1000:
                    a[-1].append(value_u)

            b.append(0)
            a.append([])
            for j in range(len(theta_coeffs)):
                if theta_coeffs[j][0] == "":
                    continue
                value_theta = eval_singularity(theta_coeffs[j], x=x)
                if theta_coeffs[j][0] >= 1000:
                    b[-1] -= value_theta
                elif theta_coeffs[j][0] < 1000:
                    a[-1].append(value_theta)

        elif fixtures[i][0] == "Pinned/Roller":
            b.append(0)
            a.append([])

            x = fixtures[i][1]  # location of fixture
            for j in range(len(u_coeffs)):
                if u_coeffs[j][0] == "":
                    continue
                value_u = eval_singularity(u_coeffs[j], x)
                if u_coeffs[j][0] >= 1000:
                    b[-1] -= value_u
                elif u_coeffs[j][0] < 1000:
                    a[-1].append(value_u)

    # gather only the equations you need to solve for unknowns
    real_a = []
    real_b = []
    num_unknowns = len(a[0])
    for i in range(num_unknowns):
        real_a.append(a[i])
        real_b.append(b[i])

    #coeffs = []
    if selection == "A":
        return real_a
    elif selection == "B":
        return real_b


def evaluate_beam_value(coeffs, x_val):
    y_val = 0
    for j in range(len(coeffs)):
        y_val += eval_singularity(coeffs[j], x_val)
    return y_val


def create_points(coeffs, overall_length, num_points, selection='y'):
    x_increment = overall_length / num_points
    x_val = 0
    y_vals = []
    x_vals = []
    for i in range(num_points+1):
        y_val = evaluate_beam_value(coeffs, x_val)
        y_vals.append(y_val)
        x_vals.append(x_val)
        x_val += x_increment
    if selection == 'x':
        return x_vals
    else:
        return y_vals
    
    
def find_new_coeffs(forces, unknowns, youngs_modulus, moment_of_inertia, solns, overall_length, selection):
    id_val = 1000
    n = -1
    p_coeffs = []  # id, coefficient(value), location, exponent

    for i in range(len(forces)):
        if forces[i][0] == "Concentrated Force":
            n = -1
            p_coeffs.append([id_val, forces[i][3], forces[i][1], n])
            id_val += 1
        elif forces[i][0] == "Concentrated Moment":
            n = -2
            p_coeffs.append([id_val, forces[i][3], forces[i][1], n])
            id_val += 1
        elif forces[i][0] == "Constant Distributed Load":
            n = 0
            p_coeffs.append([id_val, forces[i][3], forces[i][1], n])
            id_val += 1
            if forces[i][2] != overall_length:
                p_coeffs.append([id_val, -1 * forces[i][3], forces[i][2], n])
                id_val += 1
        elif forces[i][0] == "Linear Distributed Load":
            n = 1
            m = forces[i][3] / (forces[i][2] - forces[i][1])
            p_coeffs.append([id_val, m, forces[i][1], n])
            id_val += 1
            if forces[i][2] < overall_length:
                p_coeffs.append([id_val, -1 * m, forces[i][2], n])
                id_val += 1
                p_coeffs.append([id_val, -1 * forces[i][3], forces[i][2], 0])
                id_val += 1
        elif forces[i][0] == "None":
            continue

    for i in range(len(unknowns)):
        if unknowns[i][1] == "Moment":
            n = -2
            p_coeffs.append([unknowns[i][0], solns[i], unknowns[i][2], n]) #solns[i][0]]?
        elif unknowns[i][1] == "Force y":
            n = -1
            p_coeffs.append([unknowns[i][0], solns[i], unknowns[i][2], n]) #solns[i][0]]?
        else:
            continue

    v_coeffs = []
    v_coeff = []
    m_coeffs = []
    m_coeff = []
    theta_coeffs = []
    theta_coeff = []
    u_coeffs = []
    u_coeff = []

    # Add a1 and a2 to theta and u. Assume a1 and a2 = 1 for now, will solve to find them later.
    theta_coeffs.append([1, solns[0] / (youngs_modulus * moment_of_inertia), -1, 0])  # want EvalSingularity to return a1
    u_coeffs.append([1, solns[0] / (youngs_modulus * moment_of_inertia), 0, 1])  # want EvalSingularity to return a1*x
    u_coeffs.append([2, solns[1] / (youngs_modulus * moment_of_inertia), -1, 0])  # want EvalSingularity to return a2

    for i in range(len(p_coeffs)):
        v_coeff = integrate_singularity(p_coeffs[i])
        v_coeffs.append(v_coeff)
        m_coeff = integrate_singularity(v_coeff)
        m_coeffs.append(m_coeff)
        theta_coeff = integrate_singularity(m_coeff)
        theta_coeff[1] = theta_coeff[1] / (youngs_modulus * moment_of_inertia)
        theta_coeffs.append(theta_coeff)
        u_coeff = integrate_singularity(theta_coeff)
        u_coeffs.append(u_coeff)

    if selection == "P(x) Coefficients":
        return p_coeffs
    elif selection == "V(x) Coefficients":
        return v_coeffs
    elif selection == "M(x) Coefficients":
        return m_coeffs
    elif selection == "Theta(x) Coefficients":
        return theta_coeffs
    elif selection == "u(x) Coefficients":
        return u_coeffs

    
def solve_beam(loads_moments, fixtures, overall_length, moment_of_inertia, youngs_modulus, num_points, result_length_unit, result_force_unit):
    important_locations = locations_of_interest(loads_moments, fixtures)
    unknowns = find_unknowns(fixtures)

    p_coefficients = find_coefficients(loads_moments, unknowns, youngs_modulus, moment_of_inertia, overall_length, "P(x) Coefficients")
    #v_coefficients = find_coefficients(loads_moments, unknowns, youngs_modulus, moment_of_inertia, overall_length, "V(x) Coefficients")
    #m_coefficients = find_coefficients(loads_moments, unknowns, youngs_modulus, moment_of_inertia, overall_length, "M(x) Coefficients")
    theta_coefficients = find_coefficients(loads_moments, unknowns, youngs_modulus, moment_of_inertia, overall_length, "Theta(x) Coefficients")
    u_coefficients = find_coefficients(loads_moments, unknowns, youngs_modulus, moment_of_inertia, overall_length, "u(x) Coefficients")

    A = np.array(create_ab(fixtures, theta_coefficients, u_coefficients, p_coefficients, overall_length, "A"))
    b = np.array(create_ab(fixtures, theta_coefficients, u_coefficients, p_coefficients, overall_length, "B"))

    solns = np.linalg.solve(A, b)

    p_coefficients_new = find_new_coeffs(loads_moments, unknowns, youngs_modulus, moment_of_inertia, solns, overall_length, "P(x) Coefficients")
    v_coefficients_new = find_new_coeffs(loads_moments, unknowns, youngs_modulus, moment_of_inertia, solns, overall_length, "V(x) Coefficients")
    m_coefficients_new = find_new_coeffs(loads_moments, unknowns, youngs_modulus, moment_of_inertia, solns, overall_length, "M(x) Coefficients")
    theta_coefficients_new = find_new_coeffs(loads_moments, unknowns, youngs_modulus, moment_of_inertia, solns, overall_length, "Theta(x) Coefficients")
    u_coefficients_new = find_new_coeffs(loads_moments, unknowns, youngs_modulus, moment_of_inertia, solns, overall_length, "u(x) Coefficients")
    
    beam_x_values = create_points(p_coefficients_new, overall_length, num_points, 'x')
    
    y_force_plot = create_points(p_coefficients_new, overall_length, num_points)
    y_shear_plot = create_points(v_coefficients_new, overall_length, num_points)
    y_moment_plot = create_points(m_coefficients_new, overall_length, num_points)
    y_angle_plot = create_points(theta_coefficients_new, overall_length, num_points)
    y_deflection_plot = create_points(u_coefficients_new, overall_length, num_points)
    y_deflection_plot = np.array(y_deflection_plot)
    max_deflection_idx = np.argmax(np.absolute(y_deflection_plot))
    max_deflection = y_deflection_plot[max_deflection_idx]
    max_deflection_pos = beam_x_values[max_deflection_idx]

    reactions = [row + [solns[i]] for i, row in enumerate(unknowns)] # add the reaction value to each row of the unknowns list
    results = {
        'fixtures': fixtures,
        'loads_moments': loads_moments,
        'reactions': reactions,
        'important_locations': important_locations,
        'beam_x_values': beam_x_values,
        'y_force_plot': y_force_plot,
        'y_shear_plot': y_shear_plot,
        'y_moment_plot': y_moment_plot,
        'y_angle_plot': y_angle_plot,
        'y_deflection_plot': y_deflection_plot,
        'max_deflection': max_deflection,
        'max_deflection_pos': max_deflection_pos,
        'length_unit': result_length_unit,
        'force_unit': result_force_unit
    }
    return results


def add_beam_context(fig, results:dict, row_num, col_num):
    """Adds the flat beam line."""
    flat_beam = np.zeros(np.shape(results['beam_x_values']))
    fig.add_trace(go.Scatter(
        x=results['beam_x_values'], y=flat_beam, 
        mode='lines', line=dict(color='black', width=5), 
        name='Beam', hoverinfo='none', showlegend=False
    ), row=row_num, col=col_num)
    for fixture in results['fixtures']:
        if fixture[0] == "Pinned/Roller":
            fixture_hover_text = "Pinned/Roller Support: "
            for reaction in results['reactions']:
                if reaction[0] > 2: # skip integration constants
                    if reaction[2] == fixture[1]: # reaction and fixture at same location
                        fixture_hover_text += "<br>Force = " + f"{reaction[3]:.4f}" + " " + results['force_unit']
            fig.add_trace(go.Scatter(
                x=[fixture[1]], y=[0],
                marker_symbol="arrow-up",
                marker_color="black",
                marker_size=15,
                showlegend=False,
                hoverinfo="text",
                hovertext=[fixture_hover_text]
            ), row=row_num, col=col_num)
        if fixture[0] == "Fixed":
            fixture_hover_text = "Fixed Support: "
            for reaction in results['reactions']:
                if reaction[0] > 2: # skip integration constants
                    if reaction[2] == fixture[1]: # reaction and fixture at same location
                        if reaction[1] == 'Moment':
                            fixture_hover_text += "<br>Moment = " + f"{reaction[3]:.4f}" + " " + results['force_unit'] + "*" + results['length_unit']
                        if reaction[1] == 'Force y':
                            fixture_hover_text += "<br>Force = " + f"{reaction[3]:.4f}" + " " + results['force_unit']
            fig.add_trace(go.Scatter(
                x=[fixture[1]], y=[0],
                marker_symbol="square",
                marker_color="black",
                marker_size=15,
                showlegend=False,
                hoverinfo="text",
                hovertext=[fixture_hover_text]
            ), row=row_num, col=col_num)
    #4. Add loads and moments
    for load in results['loads_moments']:
        load_value = f"{load[3]:.4f}"
        if load[0] == 'Concentrated Force':
            fig.add_trace(go.Scatter(
                x=[load[1]],
                y=[0],
                mode="markers+text",
                marker=dict(size=5, opacity=0),
                text=["↑" if load[3] > 0 else "↓"],
                textposition="top center",
                textfont=dict(size=28, color="red", weight="bold"),
                hoverinfo="text",
                hovertext=[f"Force: {load_value}"+ " " + results['force_unit']],
                showlegend=False
            ), row=row_num, col=col_num)
        if load[0] == 'Concentrated Moment':
            fig.add_trace(go.Scatter(
                x=[load[1]],
                y=[0],
                mode="markers+text",
                marker=dict(size=5, opacity=0),
                text=["↺" if load[3] < 0 else "↻"],
                textposition="middle center",
                textfont=dict(size=28, color="red", weight="bold"),
                hoverinfo="text",
                hovertext=[f"Moment: {load_value}"+ " " + results['force_unit']+ "*" + results['length_unit']],
                showlegend=False
            ), row=row_num, col=col_num)


def generate_beam_plot(results: dict, length_unit:str='m', force_unit:str='N'):
    """
    Generates a single Plotly Figure with three stacked subplots, 
    aligning zeros on dual-axis plots.
    """
    # Extract data
    beam_x_values = results['beam_x_values']
    y_force_plot = results['y_force_plot']      # Load
    y_shear_plot = results['y_shear_plot']      # Shear
    y_moment_plot = results['y_moment_plot']    # Moment
    y_angle_plot = results['y_angle_plot']      # Angle
    y_deflection_plot = results['y_deflection_plot'] # Deflection
    max_deflection_y = results['max_deflection']
    max_deflection_x = results['max_deflection_pos']
    fixtures = results['fixtures']
    loads = results['loads_moments']
    
    # 1. Create Subplots Layout: 3 rows, with secondary Y axis on rows 2 and 3
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=('Applied Loads', 'Shear Force & Bending Moment', 'Deflection & Angle of Deflection'),
        # Define dual-axis for rows 2 and 3
        specs=[
            [{"secondary_y": False}],
            [{"secondary_y": True}],
            [{"secondary_y": True}]
        ],
        vertical_spacing=0.1
    )

    # --- ROW 1: Distributed Load ---
    
    # Add Distributed Load (Fill area is a good representation)
    load_name = f"Distributed Load ({force_unit})"
    fig.add_trace(go.Scatter(
        x=beam_x_values, y=y_force_plot,
        fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.4)',
        mode='lines', line=dict(color='red', width=2),
        name=load_name, showlegend=False
    ), row=1, col=1)
    
    # Add a flat beam line for context
    add_beam_context(fig, results, 1, 1)

    # --- ROW 2: Shear & Bending Moment ---

    # Calculate zero-aligned ranges
    try:
        range_s = np.ptp(y_shear_plot)
        min_s = np.min(y_shear_plot) - 0.1*range_s
        max_s = np.max(y_shear_plot) + 0.1*range_s
        range_m = np.ptp(y_moment_plot)
        min_m = np.min(y_moment_plot) - 0.1*range_m
        max_m = np.max(y_moment_plot) + 0.1*range_m
        (range_s_min, range_s_max), (range_m_min, range_m_max) = align_zeros_plotly(min_s, max_s, min_m, max_m)
    except:
        (range_s_min, range_s_max), (range_m_min, range_m_max)= (-10, 10), (-10, 10)
    
    # Shear (Primary Y)
    shear_name = f"Shear Force ({force_unit})"
    fig.add_trace(go.Scatter(
        x=beam_x_values, y=y_shear_plot, 
        mode='lines', line=dict(color='blue', width=2), 
        name=shear_name
    ), row=2, col=1, secondary_y=False)

    # Moment (Secondary Y)
    bending_name = f"Bending Moment ({force_unit}*{length_unit})"
    fig.add_trace(go.Scatter(
        x=beam_x_values, y=y_moment_plot, 
        mode='lines', line=dict(color='green', width=2), 
        name=bending_name
    ), row=2, col=1, secondary_y=True)
    
    # Add a flat beam line for context
    add_beam_context(fig, results, 2, 1)

    # --- ROW 3: Deflection & Angle of Deflection ---
    
    # Calculate zero-aligned ranges
    try:
        range_d = np.ptp(y_deflection_plot)
        min_d = np.min(y_deflection_plot) - 0.1*range_d
        max_d = np.max(y_deflection_plot) + 0.1*range_d
        range_a = np.ptp(y_angle_plot)
        min_a = np.min(y_angle_plot) - 0.1*range_a
        max_a = np.max(y_angle_plot) + 0.1*range_a
        (range_d_min, range_d_max), (range_a_min, range_a_max) = align_zeros_plotly(min_d, max_d, min_a, max_a)
    except:
        (range_d_min, range_d_max), (range_a_min, range_a_max) = (-10, 10), (-10, 10)
        

    # Deflection (Primary Y)
    deflection_name = f"Deflection ({length_unit})"
    fig.add_trace(go.Scatter(
        x=beam_x_values, y=y_deflection_plot, 
        mode='lines', line=dict(color='purple', width=3), 
        name=deflection_name
    ), row=3, col=1, secondary_y=False)

    # Angle (Secondary Y)
    fig.add_trace(go.Scatter(
        x=beam_x_values, y=y_angle_plot, 
        mode='lines', line=dict(color='red', width=2), 
        name='Angle of Deflection (rad)'
    ), row=3, col=1, secondary_y=True)
    
    # Max Deflection Point (on the Primary Y-axis of Row 3)
    fig.add_trace(go.Scatter(
        x=[max_deflection_x], y=[max_deflection_y],
        mode='markers',
        marker=dict(symbol='x', size=12, color='purple'),
        name='Max Deflection',
        hoverinfo='text',
        text=f'Max Deflection: {max_deflection_y:.3E}',
        showlegend=False
    ), row=3, col=1, secondary_y=False)
    
    # Add a flat beam line for context
    add_beam_context(fig, results, 3, 1)

    # Calculate X-axis ranges
    try:
        x_min = np.min(beam_x_values) - np.ptp(beam_x_values)*0.05
        x_max = np.max(beam_x_values) + np.ptp(beam_x_values)*0.05
    except:
        x_min=-0.1
        x_max=10
    # --- 4. Configure Layout and Axes ---
    fig.update_layout(
        title_text="Beam Analysis Diagrams",
        height=850,
        
        font=dict(
            family="Roboto",
            size=12,
            color="black"
        ),

        # Legend Configuration (Moved to bottom)
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),

        xaxis=dict(
            range=[x_min, x_max],
            constrain="domain",
        ),
        
        # Enforce zero alignment using the calculated ranges
        yaxis2=dict(title=shear_name, color='blue', range=[range_s_min, range_s_max], zeroline=True, zerolinecolor='black'),
        yaxis3=dict(title=bending_name, color='green', overlaying='y2', side='right', range=[range_m_min, range_m_max], zeroline=True, zerolinecolor='black'),
        
        yaxis4=dict(title=deflection_name, color='purple', range=[range_d_min, range_d_max], zeroline=True, zerolinecolor='black'),
        yaxis5=dict(title='Angle of Deflection (rad)', color='red', overlaying='y4', side='right', range=[range_a_min, range_a_max], zeroline=True, zerolinecolor='black'),
    )
    
    # Update X-axis title for the bottom plot only
    x_axis_name = f"Distance Along Beam ({length_unit})"
    fig.update_xaxes(title_text=x_axis_name, row=3, col=1)
    
    return fig


def align_zeros_plotly(min1, max1, min2, max2):
    """
    Calculates the shared y-axis range to align the zero lines of two axes.
    Returns: (range1_min, range1_max), (range2_min, range2_max)
    """
    
    # Calculate the ratio of the zero line relative to the full span for both axes
    span1 = max1 - min1
    ratio1 = -min1 / span1
    
    span2 = max2 - min2
    ratio2 = -min2 / span2
    
    # Determine the required new max and min spans to accommodate both zero ratios
    # Max span above zero needed (maximum of (total span * (1 - ratio)))
    new_max_ratio = max(1 - ratio1, 1 - ratio2)
    # Max span below zero needed (maximum of (total span * ratio))
    new_min_ratio = max(ratio1, ratio2)

    # Calculate the new symmetric ranges based on the maximum required span
    
    # Range 1 (Shear or Deflection)
    new_span1 = span1 / (ratio1 + (1 - ratio1))
    new_max1 = new_max_ratio * new_span1
    new_min1 = -new_min_ratio * new_span1
    
    # Range 2 (Moment or Angle)
    new_span2 = span2 / (ratio2 + (1 - ratio2))
    new_max2 = new_max_ratio * new_span2
    new_min2 = -new_min_ratio * new_span2
    
    return (new_min1, new_max1), (new_min2, new_max2)

