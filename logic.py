# logic library

from util import *


class Simulation:
    LED_THEMES = [
        ['⭔', '⭓'],
        ['□', '■'],
        ['◇', '◆'],
        ['⚪', '⚫'],
    ]
    TOTAL_STEPS = 0
    INITIALIZATION_STEPS = 0
    # start using initilization debug log
    DEBUG_FILE = give_path(f'{DEFAULT_DEBUG_DIRECTORY}') / 'initialization.log'
    log_disk(DEBUG_FILE, message='Opened file', timestamp=True, clear=True)
    log_disk(DEBUG_FILE, message=f'{" INITIALIZATION DEBUG ":+^50}')
    ON_CHECKPOINT = lambda x: input(x)

    @staticmethod
    def log_debug(*args, **kwargs):
        log_disk(Simulation.DEBUG_FILE, *args, **kwargs)

    def __init__(self, switches: list, led_panels: dict, theme=0):
        for s in switches:
            if not isinstance(s, Switch):
                raise ValueError(f'Simulation Switch must be of type {Switch}')
        self.switches = switches
        self.led_panels = led_panels
        self.theme = theme
        Simulation.ON_CHECKPOINT = lambda x: self.checkpoint(x)

    def checkpoint(self, message):
        self.print_leds()
        # print(f'{message}')

    def run(self, multi_switch=False, timeout=1000000):
        self.initialize()
        Gate.gate_summary()
        steps = 0
        while True:
            self.log_debug(f'{f" STABLE STATE ":=^50}\n'
                           f'{f" Simulation steps: {steps:,} (out of {Simulation.TOTAL_STEPS:,} total) ": ^50}\n'
                           f'{"=" * 50}')
            self.print_leds()

            # toggle switches
            print('\n')
            snames = f" | ".join(f"{i}: {g.name}" for i, g in enumerate(self.switches))
            self.print_leds(led_panels={snames: self.switches}, console_clear=False)
            switch_input = input(f'\nSwitch Board: ')
            toggled_switches = []
            print('\n'*10)
            if switch_input == 'q':
                quit_()
            if switch_input == 'r':
                quit_(restart=True)
            # if switch_input == '':
            #     switch_input = '1'
            if multi_switch:
                for i, switch in enumerate(switch_input):
                    try:
                        val = int(switch)
                    except ValueError:
                        print(f'Multi switch mode takes a string of 0\'s and 1\'s. Found: {switch}')
                        continue
                    if val is 1:
                        self.toggle_switch(i)
                        toggled_switches.append(self.switches[i])
            else:
                try:
                    sid = int(switch_input)
                    self.toggle_switch(sid)
                    toggled_switches.append(self.switches[sid])
                except ValueError:
                    print(f'Single switch mode takes a switch number (integer index). Found: {switch_input}')
                except IndexError:
                    print(f'Switch index out of range. Selected: {switch_input}, expected: 0-{len(self.switches)-1}')

            steps = Simulation.simulate(toggled_switches, timeout=timeout)

    def toggle_switch(self, switch_index):
            self.switches[switch_index].toggle_state()

    def print_leds(self, led_panels=None, console_clear=True):
        if console_clear:
            print('\n' * 20)
            print(f'{" LED MONITOR ":=^100}')
        if led_panels is None:
            led_panels = self.led_panels
        s = ''
        for label, leds in led_panels.items():
            s += f'\n{label}\n'
            try:
                for led in leds:
                    s += f'{Simulation.LED_THEMES[self.theme][led.state]: ^5}'
            except TypeError:
                s += f'{Simulation.LED_THEMES[self.theme][leds.state]: ^5}'
        print(s)

    @staticmethod
    def simulate(switches, timeout=1000000):
        next_frame = [*switches]
        step = 0
        while len(next_frame) > 0 and step < timeout:
            step += 1
            Simulation.TOTAL_STEPS += 1
            current_frame = next_frame
            next_frame = []

            # drive gates and prepare next frame
            for gate in current_frame:
                if gate.update_state():
                    if gate.debug:
                        Simulation.log_debug(f'[Step: {Simulation.TOTAL_STEPS}] {gate.changed_state_str}')
                    if gate.debug_checkpoint:
                        Simulation.log_debug(f'{"="*100}\n'
                                             f'{f" CHECKPOINT REACHED! ": ^100}\n'
                                             f'{f"[Step: {Simulation.TOTAL_STEPS}] {gate.changed_state_str}": ^100}\n'
                                             f'{"="*100}')
                        Simulation.ON_CHECKPOINT(f'CHECKPOINT REACHED! '
                                                 f'[Step: {Simulation.TOTAL_STEPS}] {gate.changed_state_str}')
                        gate.debug_checkpoint(f'CHECKPOINT REACHED! '
                                              f'[Step: {Simulation.TOTAL_STEPS}] {gate.changed_state_str}')
                    for output in gate.outputs:
                        if output not in next_frame:
                            next_frame.append(output)

        return step

    @staticmethod
    def initialize(cycles=1):
        for i in range(cycles):
            for gate in Gate.ALL_GATES:
                Simulation.simulate([gate])
        Simulation.log_debug(message=f'{f" Initilization steps: {Simulation.TOTAL_STEPS} ":+^50}')
        Simulation.INITIALIZATION_STEPS = Simulation.TOTAL_STEPS
        Simulation.TOTAL_STEPS = 0
        # switch to simulation debug log
        Simulation.DEBUG_FILE = give_path(f'{DEFAULT_DEBUG_DIRECTORY}') / 'simulation.log'
        log_disk(Simulation.DEBUG_FILE, message='Opened file', timestamp=True, clear=True)
        log_disk(Simulation.DEBUG_FILE, message=f'{" SIMULATION DEBUG ":+^50}')


class Gate:
    ALL_GATES = []
    DEFAULT_DEBUG = False
    TYPE_NAME = 'Base Gate - NOT RECOMMENDED: please use a sub-class of Gate'
    DEBUG_FILE = give_path(f'{DEFAULT_DEBUG_DIRECTORY}') / 'gates.log'
    log_disk(DEBUG_FILE, message='Opened file', timestamp=True, clear=True)
    log_disk(DEBUG_FILE, message=f'{" GATE DEBUG ":+^50}')

    def __init__(self, inputs=None, outputs=None, state=False, name='Unnamed',
                 debug=None, debug_checkpoint=False,
                 on_change_high=None, on_change_low=None):
        if outputs is None:
            outputs = []
        if inputs is None:
            inputs = []
        if not(on_change_high is None or callable(on_change_high)):
            raise ValueError(f'on_change_high must be callable')
        if not (on_change_low is None or callable(on_change_low)):
            raise ValueError(f'on_change_low must be callable')
        Gate.ALL_GATES.append(self)
        self.name = name
        self.state = state
        self.inputs = []
        self.outputs = []
        self.debug = debug if debug is not None else Gate.DEFAULT_DEBUG
        self.debug_checkpoint = debug_checkpoint
        self.on_change_high = on_change_high
        self.on_change_low = on_change_low
        self.connect_inputs(inputs)
        self.connect_outputs(outputs)

    def connect_inputs(self, inputs, recip=True):
        if not isinstance(inputs, list):
            inputs = [inputs]
        for inp in inputs:
            if inp not in self.inputs:
                self.inputs.append(inp)
            if recip:
                inp.connect_outputs(self, recip=False)

    def connect_outputs(self, outputs, recip=True):
        if not isinstance(outputs, list):
            outputs = [outputs]
        for out in outputs:
            if out not in self.outputs:
                self.outputs.append(out)
            if recip:
                out.connect_inputs(self, recip=False)

    def update_state(self):
        new_state = self.check_state()
        if self.state != new_state:
            if self.debug:
                self.log_debug(f'[Step: {Simulation.TOTAL_STEPS}] {self.changing_state_str}')
            self.state = new_state
            if self.on_change_high is not None and new_state:
                self.on_change_high(self.changed_state_str)
            if self.on_change_low is not None and not new_state:
                self.on_change_low(self.changed_state_str)
            return True
        return False

    def check_state(self):
        return self.state

    # useful properties

    def __int__(self):
        return int(self.state)

    def __str__(self):
        return f'{self.name} {self.__class__.TYPE_NAME}'

    @property
    def state_str(self):
        return f'[{high_low(self.state)}] {self.name} {self.__class__.TYPE_NAME}'

    @property
    def changing_state_str(self):
        return f'[{high_low(self.state)} -> {high_low(not self.state)}] {self.name}'

    @property
    def changed_state_str(self):
        return f'[{high_low(not self.state)} -> {high_low(self.state)}] {self.name}'

    @property
    def full_str(self):
        return f'{self.state_str} ' \
               f'(inputs: {", ".join(inp.short_str for inp in self.inputs)}; ' \
               f'outputs: {", ".join(out.short_str for out in self.outputs)})'

    @property
    def full_mstr(self):
        return f'{self.state_str}\n' \
               f'  ---  inputs: {", ".join(inp.short_str for inp in self.inputs)}\n' \
               f'  --- outputs: {", ".join(out.short_str for out in self.outputs)}'

    @property
    def short_str(self):
        return f'{self.name} [{high_low(self.state)}]'

    @property
    def monitor(self):
        return str(int(self.state))

    @staticmethod
    def log_debug(*args, **kwargs):
        log_disk(Gate.DEBUG_FILE, *args, **kwargs)

    @staticmethod
    def enable_debug(d: bool = True):
        Gate.DEFAULT_DEBUG = d

    @staticmethod
    def gate_summary():
        r = f'{f"="*50}\n{f"All {len(Gate.ALL_GATES)} Gates:": ^50}\n{f"="*50}'
        for g in Gate.ALL_GATES:
            if g.debug:
                r += f'\n\n{g.full_mstr}'
        Gate.log_debug(f'{r}\n{"":=<50}')


class Switch(Gate):
    TYPE_NAME = 'Switch'

    def set_state(self, state):
        if self.state == state:
            if self.debug:
                self.log_debug(f'[Step: {Simulation.TOTAL_STEPS}] {self.state_str}')
            return False
        else:
            self.state = state
            if self.debug:
                self.log_debug(f'[Step: {Simulation.TOTAL_STEPS}] {self.changing_state_str}')
            return True

    def toggle_state(self):
        return self.set_state(not self.state)

    def update_state(self):
        return True


class High(Gate):
    TYPE_NAME = 'TRUE'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = True

    def check_state(self):
        return True


class Low(Gate):
    TYPE_NAME = 'FALSE'

    def check_state(self):
        return False


class And(Gate):
    TYPE_NAME = 'AND'

    def check_state(self):
        return all([inp.state for inp in self.inputs])


class Not(Gate):
    TYPE_NAME = 'NOT'

    def check_state(self):
        return not all([inp.state for inp in self.inputs])


class Or(Gate):
    TYPE_NAME = 'OR'

    def check_state(self):
        return any([inp.state for inp in self.inputs])


class Nor(Gate):
    TYPE_NAME = 'NOR'

    def check_state(self):
        return not any([inp.state for inp in self.inputs])


class Xor(Gate):
    TYPE_NAME = 'XOR'

    def check_state(self):
        return [inp.state is True for inp in self.inputs].count(True) == 1


class Nxor(Gate):
    TYPE_NAME = 'NXOR'

    def check_state(self):
        return not [inp.state is True for inp in self.inputs].count(True) == 1


class LED(Or):
    TYPE_NAME = 'LED'
