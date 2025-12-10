from nicegui import ui

def linear_interpolation(a, b, c, d, e):
        if e == c:
            return None
        return a + (b - c) * (d - a) / (e - c)

class LinearInterpolationPage:
    def __init__(self):
        self.build_ui()
    
    def build_ui(self):
        ui.image('./icons/interpolation_diagram.png').classes('w-96')
        ui.restructured_text(''' Fill in five values and leave one blank. 
                             Click the calculate button, and the blank value will be filled in by linear interpolation.
                             
                              ''')
        
        with ui.row().classes('items-center gap-2 table-header'):
            ui.label('x').classes('w-32 text-center')
            ui.label('y').classes('w-32 text-center')
        with ui.row():
            self.x1 = ui.number().classes('w-32')
            self.y1 = ui.number().classes('w-32')
        with ui.row():
            self.x2 = ui.number().classes('w-32')
            self.y2 = ui.number().classes('w-32')
        with ui.row():
            self.x3 = ui.number().classes('w-32')
            self.y3 = ui.number().classes('w-32')
        ui.button('Calculate', on_click=self.interpolate)

    def interpolate(self):
        unknown_id = self.check_inputs()
        if unknown_id == 0:
            return
        
        x1 = self.x1.value
        x2 = self.x2.value
        x3 = self.x3.value
        y1 = self.y1.value
        y2 = self.y2.value
        y3 = self.y3.value
        
        result = None
        
        if unknown_id == 'x1':
            result = linear_interpolation(x2, y1, y2, x3, y3)
        elif unknown_id == 'x2':
            result = linear_interpolation(x1, y2, y1, x3, y3)
        elif unknown_id == 'x3':
            result = linear_interpolation(x2, y3, y2, x1, y1)
        elif unknown_id == 'y1':
            result = linear_interpolation(y2, x1, x2, y3, x3)
        elif unknown_id == 'y2':
            result = linear_interpolation(y1, x2, x1, y3, x3)
        elif unknown_id == 'y3':
            result = linear_interpolation(y1, x3, x1, y2, x2)
        
        if result is None:
            ui.notify('Cannot interpolate: division by zero')
            return
        
        if unknown_id == 'x1':
            self.x1.value = result
        elif unknown_id == 'x2':
            self.x2.value = result
        elif unknown_id == 'x3':
            self.x3.value = result
        elif unknown_id == 'y1':
            self.y1.value = result
        elif unknown_id == 'y2':
            self.y2.value = result
        elif unknown_id == 'y3':
            self.y3.value = result
    
    def check_inputs(self):
        # if there are not exactly 5 inputs return an error.
        # if there are exactly 5 numbers, return the index of the number that is None
        none_count = 0
        unknown_id = ''
        if self.x1.value == None:
            none_count += 1
            unknown_id = 'x1'
        if self.x2.value == None:
            none_count += 1
            unknown_id = 'x2'
        if self.x3.value == None:
            none_count += 1
            unknown_id = 'x3'
        if self.y1.value == None:
            none_count += 1
            unknown_id = 'y1'
        if self.y2.value == None:
            none_count += 1
            unknown_id = 'y2'
        if self.y3.value == None:
            none_count += 1
            unknown_id = 'y3'

        if none_count != 1:
            ui.notify('Please enter 5 out of the six values.')
            return 0
        else:
            return unknown_id

        