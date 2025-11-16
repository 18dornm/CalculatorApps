from nicegui import ui
from calculators.unit_conversion import convert

class UnitRow:
    def __init__(self, units: list[str]):
        with ui.row().classes('items-center gap-4'):
            self.input_left = ui.input(on_change=self.update_right).props('type=number')
            self.unit_left = ui.select(units, value=units[0], on_change=self.update_left)

            ui.label('=')

            self.input_right = ui.input(on_change=self.update_left).props('type=number')
            self.unit_right = ui.select(units, value=units[1] if len(units) >1 else units[0],
                                     on_change=self.update_right)
            
            self.result_label = ui.label('result')
    
    def update_right(self, e=None):
        """User edited the left box --> compute the right box"""
        try:
            val = float(self.input_left.value)
            target = convert(val, self.unit_left.value, self.unit_right.value)
            if target is not None:
                self.input_right.set_value(f'{target:.6g}')
                #self.input_left.set_label(f'{target:.6g}')
        except:
            pass
    
    def update_left(self, e=None):
        """User edited the right box --> compute the left box"""
        try:
            val = float(self.input_right.value)
            target = convert(val, self.unit_right.value, self.unit_left.value)
            if target is not None:
                self.input_left.set_value(f'{target:.6g}')
                #self.input_left.set_label(f'{target:.6g}')
        except:
            pass
    