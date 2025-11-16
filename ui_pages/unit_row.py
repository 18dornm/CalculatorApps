from nicegui import ui
from calculators.unit_conversion import convert

class UnitRow:

    def __init__(self, units: list[str]):

        # STATE
        self.units = units
        self.is_updating = False

        # LEFT SIDE
        with ui.row().classes('items-center gap-2'):
            ui.button(icon='content_copy', on_click=self.copy_left).props('flat dense round size=sm').classes('bg-white text-black')
            self.input_left = ui.input(value='1', on_change=self.left_changed).classes('w-24')
            self.unit_left = ui.select(options=units, value=units[0], on_change=self.right_changed)
            ui.label('=').classes('text-2xl mx-2')
            ui.button(icon='content_copy', on_click=self.copy_right).props('flat dense round size=sm').classes('bg-white text-black')
            self.input_right = ui.input(on_change=self.right_changed).classes('w-24')
            self.unit_right = ui.select(options=units, value=units[1] if len(units) > 1 else units[0],
                                        on_change=self.left_changed)

        # Initialize the right value with the conversion of 1
        self.update_right_from_left()

    # COPY EVENTS
    def copy_left(self):
        ui.run_javascript(f'navigator.clipboard.writeText("{self.input_left.value}");')
        ui.notify('Copied to Clipboard', timeout=1)

    def copy_right(self):
        ui.run_javascript(f'navigator.clipboard.writeText("{self.input_right.value}");')
        ui.notify('Copied to Clipboard', timeout=1)

    # UPDATE LEFT → RIGHT
    def left_changed(self, _=None):
        if not self.is_updating:
            self.update_right_from_left()

    # UPDATE RIGHT → LEFT
    def right_changed(self, _=None):
        if not self.is_updating:
            self.update_left_from_right()

    # INTERNAL UPDATE LEFT → RIGHT
    def update_right_from_left(self):
        try:
            left_val = float(self.input_left.value or 0)
            self.is_updating = True
            result = convert(left_val, self.unit_left.value, self.unit_right.value)
            self.input_right.value = f'{result:g}'
        except Exception:
            self.input_right.value = ''
        finally:
            self.is_updating = False

    # INTERNAL UPDATE RIGHT → LEFT
    def update_left_from_right(self):
        try:
            right_val = float(self.input_right.value or 0)
            self.is_updating = True
            result = convert(right_val, self.unit_right.value, self.unit_left.value)
            self.input_left.value = f'{result:g}'
        except Exception:
            self.input_left.value = ''
        finally:
            self.is_updating = False