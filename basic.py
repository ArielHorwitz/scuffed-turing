# basic module (basic components and circuits module)

from logic import *
import util
import time

# fixme CounterPlus needs to be fixed and made faster
"""
todo
bit shifter
multiplier
"""


class Monitor(dict):
    def output(self, width=50, show_empty=True):
        r = ''
        lines = 1
        for name, mon in self.items():
            if show_empty is False and mon.monitor == '0':
                continue
            # input(f'mon: {mon.monitor}, {type(mon.monitor)}')
            s = ' | ' if len(r) > 0 else ''
            m = f'{name}: {mon.monitor}' if show_empty else f'{name}'
            if len(r+s+m) > lines*width:
                s = '\n'
                lines += 1
            r += s + m
        return r

    def output_simple(self):
        return f'\n'.join(f'{name}: {mon.monitor}' for name, mon in self.items())


class Bus(list):
    def __init__(self, *args, bit_count=0, name='Unnamed Bus', debug=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.extend([Or(name=f'{name} line #{i}', debug=debug) for i in range(bit_count)])

    def connect_inputs(self, inp):
        if self.bit_count < len(inp):
            for i, g in enumerate(self):
                inp[i].connect_inputs([g])
        else:
            for i, g in enumerate(inp):
                self[i].connect_inputs([g])

    @property
    def bit_count(self):
        return len(self)

    @property
    def monitor(self):
        return f'TCx{str(self.tcval):0>6} [{bool2binstr(self.values)}]'

    @property
    def raw_monitor(self):
        return f'DCx{str(bool2decimal(self.values, lsbf=False)):0>6} [{bool2binstr(self.values)}]'

    @property
    def raw_monitor_lsbf(self):
        return f'DCx{str(bool2decimal(self.values, lsbf=False)):0>6} [{bool2binstr(self.values, lsbf=False)}]'

    @property
    def monitor_named(self):
        return f'[{" | ".join(f"{g.name}: {int(g.state)}" for g in self)}]'

    @property
    def monitor_named_true(self):
        return f'[{" | ".join(f"{g.name}" for g in filter(lambda x: x.state, self))}]'

    @property
    def values(self):
        return [gate.state for gate in self]

    @property
    def tcval(self):
        return tc2decimal(self.values, lsbf=True)


class Delay(And):
    def __init__(self, signal: Gate, length: int, name=f'Unnamed Delay', initial_state=False, **kwargs):
        if length < 1:
            raise ValueError(f'{name} Delay length must greater than 0 (is: {length})')
        for i in range(length-1):
            signal = And(inputs=[signal], name=f'{name} #{i}', state=initial_state, debug=False)
        super().__init__(inputs=[signal], name=f'{name} ++{length}', state=initial_state, **kwargs)


class EdgeDetector(And):
    def __init__(self, signal, sustain=1, name='Unnamed Edge Detector', **kwargs):
        if sustain < 1:
            raise ValueError(f'{name} EdgeDetector length must greater than 0 (is: {sustain})')
        sig = And(inputs=[signal], name=f'{name} Signal', debug=False)
        edge_length = Delay(signal=sig, length=sustain, name=f'{name} Edge Length', debug=False)
        decay = Not(inputs=[edge_length], name=f'{name} Decay', debug=False)
        super().__init__(inputs=[decay, sig], name=name, **kwargs)


class DLatch:
    def __init__(self, enable, data, name='Unnamed D-Latch', initial_state=False, debug=False):
        self.name = name
        self.en = And(inputs=[enable], name=f'{name} EN')
        self.d = And(inputs=[data], name=f'{name} D')
        self.d_ = Not(inputs=[self.d], name=f'{name} D_', debug=debug)
        self.s = And(name=f'{name} S', debug=debug)
        self.r = And(name=f'{name} R', debug=debug)
        self.q = Nor(name=f'{name} Q', state=initial_state, debug=debug)
        self.q_ = Nor(name=f'{name} Q_', state=not initial_state, debug=debug)

        self.s.connect_inputs([self.d, self.en])
        self.r.connect_inputs([self.d_, self.en])
        self.q.connect_inputs([self.r, self.q_])
        self.q_.connect_inputs([self.s, self.q])

        self.output = And(name=f'{name} Output', inputs=[self.q], state=initial_state)

    def __str__(self):
        return f'{self.name} ({self.output.state})'

    def _cheat_set(self, state: bool):
        self.q.state = state
        self.q_.state = not state
        self.output.state = state


class DFlipFlop:
    def __init__(self, toggle, reset, name='Unnamed DFF', initial_state=False, debug=False):
        self.name = name
        ted = EdgeDetector(toggle, name=f'{name} Toggle Pulse', debug=debug)
        red = EdgeDetector(reset, name=f'{name} Reset Pulse', debug=debug)
        rsync = Or(inputs=[ted, red], name=f'{name} Reset Sync', debug=debug)
        ssync = And(inputs=[ted], name=f'{name} Set Sync', debug=debug)
        self.s = And(name=f'{name} S', debug=False)
        self.r = And(name=f'{name} R', debug=False)
        self.q = Nxor(name=f'{name} Q', state=initial_state, debug=False)
        self.q_ = Nxor(name=f'{name} Q_', state=not initial_state, debug=False)
        self.qd = Delay(signal=self.q, length=10, initial_state=initial_state, name=f'{name} Q Delay', debug=False)
        self.q_d = Delay(signal=self.q_, length=10, initial_state=not initial_state, name=f'{name} Q_ Delay', debug=False)

        self.r.connect_inputs([rsync, self.qd])
        self.s.connect_inputs([ssync, self.q_d])
        self.q.connect_inputs([self.s, self.q_])
        self.q_.connect_inputs([self.r, self.q])

        self.output = And(name=f'{name} Output', inputs=[self.q], state=initial_state, debug=debug)

    @property
    def monitor(self):
        # return self.debug_
        return f'{self.name} ({self.output.state})'


class JKFF(DFlipFlop):
    def __init__(self, toggle, reset, load, data, name='Unnamed JKFF', initial_state=False, debug=False):
        d = And(inputs=[data], name=f'{name} D', debug=debug)
        d_ = Not(inputs=[data], name=f'{name} D_', debug=False)
        l0 = And(inputs=[load, d_], name=f'{name} Load 0', debug=debug)
        l1 = And(inputs=[load, d], name=f'{name} Load 1', debug=debug)
        ed1 = EdgeDetector(signal=l1, name=f'{name} Load 1 Pulse', debug=False)
        ed2 = Delay(signal=ed1, length=4, name=f'{name} Load 1 Second Pulse', debug=False)
        r = Or(inputs=[reset, l0, ed1], name=f'{name} Reset', debug=debug)
        t = Or(inputs=[toggle, ed2], name=f'{name} Toggle', debug=debug)
        super().__init__(toggle=t, reset=r, name=f'{name} DFF', initial_state=initial_state)


class BSB(Bus):
    # Bi-State Buffer
    def __init__(self, b: Bus, oe: Gate, name=f'Unnamed BSB'):
        super().__init__([And(inputs=[g, oe], name=f'{name} #{i}') for i, g in enumerate(b)],
                         name=f'{name}')


class Sustain(And):
    def __init__(self, signal, length, name=f'Unnamed Sustain'):
        sig = EdgeDetector(signal=signal, name=f'{name} Signal Pulse')
        decay = Delay(signal=sig, length=length, name=f'{name} Decay')
        self.dff = DFlipFlop(toggle=sig, reset=decay, name=f'{name} DFF')
        super().__init__(inputs=[self.dff.output], name=f'{name}')


class Clock(And):
    def __init__(self, enable: Gate, half_cycle_time: int, name=f'Unnamed Clock', real_time=False):
        self.real_time = real_time
        self.enable = And(inputs=[enable], name=f'{name} Enable')
        self.initial_cycle = EdgeDetector(signal=self.enable, name=f'{name} Initial Cycle')
        new_cycle = Or(inputs=[self.initial_cycle], name=f'{name} New Cycle')
        self.cycle_pulse = And(inputs=[self.enable, new_cycle], name=f'{name} Cycle Pulse')
        new_cycle_delay = Delay(signal=self.cycle_pulse, length=(half_cycle_time*2),
                                name=f'{name} New Cycle Delay')
        new_cycle_delay.connect_outputs([new_cycle])
        sus = Sustain(signal=self.cycle_pulse, length=half_cycle_time,
                      name=f'{name} Cycle Sustain')
        super().__init__(inputs=[sus],
                         name=f'{name} @{half_cycle_time*2} S/C',
                         debug_checkpoint=print if real_time <= 0 else self.real_time_pause,
                         on_change_high=input if self.real_time < 0 else None)

    def real_time_pause(self, message):
        print(message)
        time.sleep(self.real_time)


class Register:
    def __init__(self, bit_count, ri: Gate, ro: Gate, ibus: Bus, obus=None,
                 name='Unnamed Register'):
        if obus is None:
            obus = Bus()
        if ibus.bit_count < bit_count:
            raise ValueError(f'{name} in bus ({ibus.bit_count}-bit) smaller than register ({bit_count}-bit)!')
        self.name = name
        self.ri = EdgeDetector(signal=ri, name=f'{name} IE ED')
        self.d_latches = [DLatch(name=f'{name} DLatch #{i}', enable=self.ri, data=ibus[i]
                                 ) for i in range(bit_count)]
        self.memory = Bus([dl.output for dl in self.d_latches])
        self.outputs = Bus([And(inputs=[ro, self.d_latches[i].output], name=f'{name} Out #{i}')
                            for i in range(bit_count)])
        for i, g in enumerate(obus):
            g.connect_inputs(self.outputs[i])

    @property
    def monitor(self):
        return f'{self.memory.monitor}'

    @property
    def raw_monitor_lsbf(self):
        return f'{self.memory.raw_monitor_lsbf}'

    @property
    def tcval(self):
        return self.memory.tcval

    def _cheat_set(self, values):
        for i, v in enumerate(values):
            self.d_latches[i]._cheat_set(v)
            self.memory[i].state = v
        Simulation.simulate([*self.memory])


class BitShifter(BSB):
    def __init__(self, input_bus, sl1, sl8, sr1, sr8, name=f'Unnamed Shift Register'):
        empty = Low(name=f'{name} Empty bit')
        empty8 = [empty for i in range(8)]
        en = Xor(inputs=[sl1, sl8, sr1, sr8], name=f'{name} EN')
        ibus = BSB(b=input_bus, oe=en, name=f'{name} Input Bus')
        self.sl1 = BSB(b=Bus([empty, *ibus[:-1]]), oe=sl1, name=f'{name} Shifted Left 1')
        self.sl8 = BSB(b=Bus([*empty8, *ibus[:-8]]), oe=sl8, name=f'{name} Shifted Left 8')
        self.sr1 = BSB(b=Bus([*ibus[1:], empty]), oe=sr1, name=f'{name} Shifted Right 1')
        self.sr8 = BSB(b=Bus([*ibus[8:], *empty8]), oe=sr8, name=f'{name} Shifted Right 8')

        self.muxer = Bus(bit_count=ibus.bit_count, name=f'{name} Output Muxer Bus')
        super().__init__(b=self.muxer, oe=en, name=name)

        for b in [self.sl1, self.sl8, self.sr1, self.sr8]:
            self.muxer.connect_inputs(b)

        self.popped = Or(inputs=[
            And(inputs=[sl1, self[-1]], name=f'{name} SL1 popped'),
            And(inputs=[sl8, self[-8]], name=f'{name} SL8 popped'),
            And(inputs=[sr1, self[0]], name=f'{name} SR1 popped'),
            And(inputs=[sr8, self[7]], name=f'{name} SR8 popped'),
        ], name=f'{name} Popped bit')


class CounterPlus:
    CASCADE_DELAY = 11

    def __init__(self, signal: Gate, reset: Gate, load: Gate, d: Bus,
                 name=f'Unnamed Counter Plus', debug=False):
        self.data = Bus([And(inputs=[d[i]], name=f'D#{i}') for i in range(d.bit_count)])
        signal_pulse = EdgeDetector(signal=signal, sustain=5, name=f'{name} Initial Signal Pulse')
        reset_pulse = EdgeDetector(reset, sustain=5, name=f'{name} Reset pulse')
        load_pulse = EdgeDetector(signal=load, sustain=5, name=f'{name} Load pulse')
        cascading_signal = High(name=f'{name} 0-th cascading signal')

        self.jkffs = Bus()
        self.outputs = Bus()
        for i in range(d.bit_count):
            dis = Delay(signal=signal_pulse, length=(i*CounterPlus.CASCADE_DELAY)+1, name=f'{name} Delayed IS#{i}')
            css = And(inputs=[dis, cascading_signal], name=f'{name} Cascading Signal Sync #{i}')
            c = JKFF(toggle=css, reset=reset_pulse, load=load_pulse, data=self.data[i],
                     name=f'{name} JKFF#{i}', debug=debug)
            cascading_signal = EdgeDetector(signal=Not(inputs=[c.output], debug=debug,
                                                       name=f'{name} Cascading Signal inverter #{i+1}'),
                                            name=f'{name} Cascading Signal Pulse #{i+1}')
            self.jkffs.append(c)
            self.outputs.append(And(inputs=[c.output], name=f'{name} bit#{i}'))

    @property
    def monitor(self):
        return self.outputs.raw_monitor_lsbf


class Counter(CounterPlus):
    def __init__(self, signal, bit_count, reset=Low(), name='Unnamed Counter'):
        super().__init__(signal=signal, reset=reset, load=Low(),
                         d=Bus(bit_count=bit_count, name=f'{name} Unused load data bus'),
                         name=f'{name}')


class HalfAdder:
    def __init__(self, i1, i2, name='Unnamed Half Adder'):
        self.sum = Xor(name=f'{name} Sum', inputs=[i1, i2])
        self.cout = And(name=f'{name} Cout', inputs=[i1, i2])


class FullAdder:
    def __init__(self, i1, i2, cin, name='Unnamed Full Adder'):
        self.half_adder = HalfAdder(name=f'{name} half adder', i1=i1, i2=i2)
        self.sum = Xor(name=f'{name} Sum')
        self.carry = And(name=f'{name} Carry')
        self.cout = Or(name=f'{name} Cout')
        self.sum.connect_inputs([cin, self.half_adder.sum])
        self.carry.connect_inputs([cin, self.half_adder.sum])
        self.cout.connect_inputs([self.carry, self.half_adder.cout])


class BaseDecoder:
    def __init__(self, d: Gate, en: Gate, name=f'Unnamed BaseDecoder', address='0', debug=False):
        self.d_ = Not(name=f'{name} D_', inputs=[d], state=True, debug=debug)
        self.o0 = And(name=f'{name} O#0', inputs=[self.d_, en], debug=debug)
        self.o1 = And(name=f'{name} O#1', inputs=[d, en], debug=debug)
        self.o0.address = f'{address}0'
        self.o1.address = f'{address}1'


class Decoder:
    def __init__(self, address_input: Bus, name=f'Unnamed Decoder'):
        bit_count = len(address_input)

        def make_sub_decoder(bit_depth, en0, en1, address=''):
            if bit_depth < bit_count:
                a = f'{address}0'
                new_sub_decoder0 = BaseDecoder(name=f'{name} sub #{a}', d=address_input[bit_depth], en=en0, address=a)
                o0 = make_sub_decoder(bit_depth+1, new_sub_decoder0.o0, new_sub_decoder0.o1, a)
                a = f'{address}1'
                new_sub_decoder1 = BaseDecoder(name=f'{name} sub #{a}', d=address_input[bit_depth], en=en1, address=a)
                o1 = make_sub_decoder(bit_depth+1, new_sub_decoder1.o0, new_sub_decoder1.o1, a)
                return [*o0, *o1]
            return en0, en1

        self.base = BaseDecoder(
            name=f'{name} base',
            d=address_input[0],
            en=High(name=f'{name} base enable'),
            address='0')
        self.outputs = Bus(make_sub_decoder(1, self.base.o0, self.base.o1),
                           name=f'{name} Output Bus')

    @property
    def monitor(self):
        r = " | ".join(f"{g.address}" for g in filter(lambda x: x.state, self.outputs))
        return f'Ax{binstr2decimal(r, lsbf=False):0>6}'

    @property
    def address(self):
        return binstr2decimal([*filter(lambda x: x.state, self.outputs)][0].address, lsbf=True)


class TruthTable:
    def __init__(self, data_input: Bus, table: list, name=f'Unnamed TruthTable'):
        # decoder takes msbf for some reason... ignoring this will bite me in the ass i know
        self.decoder = Decoder(address_input=Bus(reversed(data_input)), name=f'{name} Decoder')

        self.outputs = Bus(bit_count=len(table[0]), name=f'{name} Output Bus')

        for i, row in enumerate(table):
            for j, column in enumerate(row):
                if column:
                    self.decoder.outputs[i].connect_outputs([self.outputs[j]])

    @property
    def monitor(self):
        return f'{self.decoder.monitor} : {self.outputs.raw_monitor_lsbf}'
