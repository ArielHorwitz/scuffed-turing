# builds module (custom circuits and machines)


from basic import *

# todo
"""
I/O:
interrupt (clock counter control)
controllers (scanner, keypad, printer, monitor)

ALU:
comparisons: zero, equal, greater/less than
boolean operations
bit shift operations
multiplication


jump and link
"""


# Assembled Program (msbf)
HARDCODED_RAM = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # JMP 4
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # var op
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # var count
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # var result
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # PIJ 1
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # ATR 1
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # PIJ 2
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # ATR 2
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # LPK 0
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # RTJ 2
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # SFL
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],  # JCP 20
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # RTJ 2
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # LPK 1
    [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # STR 2
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # RTJ 03
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # RTK 01
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # ATR 3
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # NAI 0
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # JMP 8
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # HLT 3
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],  # HLT 18
]
# Reverse the words as we hard code the RAM msbf but the machine reads lsbf
HARDCODED_RAM = [
    [*reversed(rl)] for rl in HARDCODED_RAM
]
CLOCK_CYCLE = 0


class TuringComplete:


    def __init__(self):
        self.power_switch = Switch(name='POWER SWITCH')
        self.initialize = EdgeDetector(signal=self.power_switch, name=f'Initialization Pulse')
        run_switch_delay = Delay(signal=self.power_switch, length=400, name=f'RUN Flag Delay')
        self.run_switch = And(inputs=[run_switch_delay], name=f'RUN Flag')
        self.clock_circuit = Clock(enable=self.run_switch, half_cycle_time=200, name=f'Main Clock Circuit',
                                   real_time=CLOCK_CYCLE,
                                   )
        self.clock = And(inputs=[self.clock_circuit], name=f'Main Clock', debug=True)
        self.mcc = Counter(self.clock, bit_count=16, name='Main Clock Counter')
        self.main_bus = Bus(name='Main Bus', bit_count=16)

        # port out
        self.po = Or(name='PO')
        self.regpo = Register(
            name='Port Out Register', bit_count=16,
            ri=And(inputs=[self.po, self.clock]), ro=Low(),
            ibus=self.main_bus
        )

        # port in
        self.port_switches = Bus([Switch(name=f'PI#{i}') for i in range(16)])
        self.pi = Or(name='PI')
        self.regpi = Register(
            name='Port In Register', bit_count=16,
            ro=And(inputs=[self.pi]), ri=Not(inputs=self.clock),
            ibus=self.port_switches, obus=self.main_bus,
        )

        # register j
        self.ji = Or(name='JI')
        self.jo = Or(name='JO')
        self.regj = Register(
            name='Register J', bit_count=16,
            ri=And(name='JIE', inputs=[self.ji, self.clock]),
            ro=And(name='JOE', inputs=[self.jo]),
            ibus=self.main_bus, obus=self.main_bus)

        # register k
        self.ki = Or(name='KI')
        self.ko = Or(name='KO')
        self.regk = Register(
            name='Register K', bit_count=16,
            ri=And(name='KIE', inputs=[self.ki, self.clock]),
            ro=And(name='KOE', inputs=[self.ko]),
            ibus=self.main_bus, obus=self.main_bus)

        # Main Control Unit
        # Gate.enable_debug()
        self.mcu = Control(init_signal_pulse=self.initialize,
                           clock=self.clock,
                           main_bus=self.main_bus,
                           name=f'Main Control Unit')
        # Gate.enable_debug(False)
        # self.mcu.control_register.outputs[1].mon = self.monitor
        self.run_switch.connect_inputs([self.mcu.run_flag])
        self.ji.connect_inputs([self.mcu.control_word[13]])
        self.jo.connect_inputs([self.mcu.control_word[14]])
        self.ki.connect_inputs([self.mcu.control_word[15]])
        self.ko.connect_inputs([self.mcu.control_word[16]])
        self.po.connect_inputs([self.mcu.control_word[19]])
        self.pi.connect_inputs([self.mcu.control_word[20]])

        ra = self.mcu.control_word[10]
        ri = self.mcu.control_word[11]
        ro = self.mcu.control_word[12]
        self.ram = RAM(name='Main RAM',
                       address_bitspace=8,
                       byte_size=16,
                       b=self.main_bus,
                       ai=And(inputs=[ra, self.clock], name='RAIE'),
                       ie=And(inputs=[ri, self.clock], name='RIE'),
                       oe=And(inputs=[ro], name='ROE'),
                       )

        # ALU
        self.alu = ALU(ra=self.regj.memory, rb=self.regk.memory,
                  sub=self.mcu.control_word[18], oe=self.mcu.control_word[17],
                  output=self.main_bus, name=f'ALU')
        self.mcu.flags_input.connect_inputs([self.alu.zero, self.alu.overflow, self.alu.carry, self.alu.sign])

    def machine(self):
        return {
            'switches': [self.power_switch, *self.port_switches[:8]],
            'led_panels': {
                f' CLK| RUN|{"|".join(f"{g.name: ^4}" for g in self.mcu.flags)}': [self.clock, self.mcu.run_flag, *self.mcu.flags],
                'Main Clock Counter': self.mcc.outputs,
                'PIX': self.mcu.pix.outputs,
                'MIX': self.mcu.mix.outputs,
                '|'.join(f'{g.name: ^4}' for g in self.mcu.control_word): self.mcu.control_word,
                'Instruction Register': self.mcu.ir.outputs,
                'Main Bus': self.main_bus,
                'ALU': self.alu.sum,
                'REG J': self.regj.memory,
                'REG K': self.regk.memory,
                'RAM Address': self.ram.address_register.outputs,
                'RAM Contents': self.ram.selected,
                'Port IN': self.regpi.memory,
                '\n\nPort OUT': self.regpo.memory,
            }
        }


class RAM:
    def __init__(self, byte_size: int, address_bitspace: int, b: Bus,
                 ai: Gate, ie: Gate, oe: Gate, name=f'Unnamed RAM'):
        self.address_register = Register(name=f'{name} Address Register', bit_count=address_bitspace,
                                         ri=ai, ro=High(name=f'{name} Address Register OE'),
                                         ibus=Bus(b[:address_bitspace])
                                         )
        self.address_decoder = Decoder(address_input=self.address_register.outputs, name=f'{name} Decoder')
        self.registers = {}
        self.ie = And(name=f'{name} IE', inputs=[ie])
        self.oe = And(name=f'{name} OE', inputs=[oe])
        self.selected = Bus(bit_count=16, name=f'{name} Selected Outputs')
        self.outputs = BSB(b=self.selected, oe=self.oe, name=f'{name} Outputs')
        b.connect_inputs(self.outputs)
        for address_selector in self.address_decoder.outputs:
            a = address_selector.address
            rie = And(name=f'{name} @{a} IE', inputs=[self.ie, address_selector])
            roe = And(name=f'{name} @{a} OE', inputs=[address_selector])
            new_reg = Register(
                bit_count=byte_size,
                ri=rie,
                ro=roe,
                ibus=b,
                obus=self.selected,
                name=f'{name} @{a} Register'
            )
            self.registers[a] = new_reg

        self.sorted_registers = sorted([(a, r) for a, r in self.registers.items()],
                                       key=lambda x: binstr2decimal(x[0], lsbf=True))

        # todo fixme this is cheating! this will be replaced by the file scanner
        for i, v in enumerate(HARDCODED_RAM):
            self.sorted_registers[i][1]._cheat_set(v)

    def debug(self, m):
        print(self.monitor)

    @property
    def monitor(self):
        a = f'Ax{str(self.address_register.memory.raw_monitor)[3:]} : {self.sorted_registers[self.address_decoder.address][1].monitor}'
        r = ''.join(f'\n{str(binstr2decimal(a_, lsbf=True)):0>4}: '
                    f'{r_.monitor}' for a_, r_ in self.sorted_registers[:16])
        a_, r_ = self.sorted_registers[-1]
        r += f'\n...\n{str(binstr2decimal(a_, lsbf=True)):0>4}: {r_.monitor}'
        return a+r


class ALU:
    def __init__(self, ra: Bus, rb: Bus, sub: Gate, oe: Gate, output: Bus, name='Unnamed ALU'):
        bit_count = min(ra.bit_count, rb.bit_count)
        self.name = name
        ra = Bus([And(inputs=[ra[i]], name=f'{name} Input sync #{i}') for i in range(bit_count)])
        self.oe = And(name=f'{name} OE', inputs=[oe])
        self.rb_sub_inverter = Bus([Xor(inputs=[sub, digit], name=f'{name} RB sub inverter') for digit in rb])
        self.adders = Bus(name=f'{name} adders bus')
        self.sum = Bus(name=f'{name} sum bus')
        self.outputs = Bus(name=f'{name} output bus')
        carry = sub
        for i in range(bit_count):
            new_adder = FullAdder(i1=ra[i], i2=self.rb_sub_inverter[i], cin=carry, name=f'{name} full adder #{i}')
            carry = new_adder.cout
            new_output = And(name=f'{name} OE #{i}', inputs=[self.oe, new_adder.sum], outputs=output[i])
            self.adders.append(new_adder)
            self.sum.append(new_adder.sum)
            self.outputs.append(new_output)

        # todo add bitwise operations
        # bit shifter
        self.bit_shifting_control = Bus([Or(name=f'{i}') for i in range(4)])
        self.bit_shifter = BitShifter(self.sum, *self.bit_shifting_control, name=f'{name} BitShifter')

        # flags
        # todo add positive / negative flags
        same_sign = Nxor(name=f'{name} operands same sign', inputs=[ra[-1], self.rb_sub_inverter[-1]])
        opposite_sign = Xor(name=f'{name} operand/result opposite sign', inputs=[ra[-1], self.adders[-1].sum])
        self.overflow = And(inputs=[same_sign, opposite_sign], name=f'{name} Overflow bit')
        self.zero = Nor(inputs=self.sum, name=f'{name} Zero bit')
        self.carry = And(inputs=[carry], name=f'{name} Carry bit')
        self.sign = And(inputs=[self.sum[-1]], name=f'{name} Sign bit')
        self.parity = Low(name=f'{name} UNIMPLEMENTED Parity bit')
        # todo add parity bit

    @property
    def monitor(self):
        return f'{Bus([a.sum for a in self.adders]).monitor} | AOF: {self.overflow.monitor}'


class Control:
    # Opcodes
    """
    0000 EOI (End of Instruction)
    0001 SFL (Set Flags)
    0010 LPJ (Load parameter to J)
    0011 LPK (Load parameter to K)
    0100 ATR (ALU to RAM @parameter)
    0101 STR (SUB to RAM @parameter)
    0110 RTJ (RAM @parameter to J)
    0111 RTK (RAM @parameter to K)
    1000 JMP (Jump to line @parameter)
    1001 JMR (Jump to line @RAM @parameter)
    1010 JCP (Jump Conditional to line @parameter) (if carry flag is set)
    1011 JCR (Jump Conditional to line @RAM @parameter) (if carry flag is set)
    1100 PIJ (parameter to Port Out, and Port In to J)
    1101 JTO (J to Port Out)
    1110 ITJ (Port In to J)
    1111 HLT (Halt)
    """
    # Control Word bits
    """
    #   00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
    #   H  CO CI CC CN II IO SF PA PB RA RI RO JI JO KI KO AO AS PO PI
    """
    # Machine Code Table composed of opcode-independent and opcode-specific microinstructions:
    GLOBAL_MICROI = [
        #   01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
        #   CO CI CC CN II IO SF PA PB RA RI RO JI JO KI KO AO AS PO PI
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    OP_CODE_MICROI = [
        # 0000 NAI
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 0001 SFL
        [
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 0010 LPJ
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 0011 LPK
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        ],
        # 0100 ATR
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        ],
        # 0101 STR
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        ],
        # 0110 RTJ
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 0111 RTK
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        ],
        # 1000 JMP
        [
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 1001 JMR
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 1010 JCP
        [
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 1011 JCR
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        # 1100, PIJ
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        ],
        # 1101 JTO
        [
            #   01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
            #   CO CI CC CN II IO SF PA PB RA RI RO JI JO KI KO AO AS PO PI
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        ],
        # 1110, ITJ
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        ],
        # 1111 HLT
        [
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ]
    MACHINE_CODE_TABLE = []
    for microinstructions_list in OP_CODE_MICROI:
        microinstruction_table = [
            *GLOBAL_MICROI,
            *microinstructions_list,
        ]
        for i in range(8 - len(microinstruction_table)):
            microinstruction_table.append([0 for j in range(len(microinstruction_table[0]))])
        MACHINE_CODE_TABLE.extend(microinstruction_table)

    def __init__(self, init_signal_pulse, clock, main_bus, name=f'Unnamed Contol Unit'):
        clock_ = Not(inputs=[clock], name=f'{name} CLK_')
        ctl = ['HL', 'CO', 'CI', 'CC', 'CN', 'II', 'IO', 'SF',
               'PA', 'PB', 'RA', 'RI', 'RO', 'JI', 'JO', 'KI',
               'KO', 'AO', 'AS', 'PO', 'PI']

        self.control_word_setup = Bus([
            Or(name=f'{n}') for i, n in enumerate(ctl)], name=f'{name} Control Word Bus Setup')
        self.control_word = Bus([And(name=g.name) for g in self.control_word_setup], name=f'{name} Control Word Bus')
        mix_reset = And(inputs=[
            Nor(inputs=self.control_word, name=f'{name} Empty Control'),
            Delay(signal=EdgeDetector(signal=clock, name=f'{name} Delayed Clock Pulse'), length=30, name=f'{name} MIX Reset Delay')
        ], name=f'{name} MIX Reset')
        self.control_register = Register(bit_count=len(ctl),
                                         ri=Or(
                                             inputs=[EdgeDetector(signal=clock_, name=f'{name} Set Control Word pulse'), init_signal_pulse],
                                             name=f'{name} Set Control Word'),
                                         ro=High(),
                                         ibus=self.control_word_setup,
                                         obus=self.control_word,
                                         name=f'{name} Control Word Register')
        self.flags = Bus([
            And(name=f'FZ'),  # zero
            And(name=f'FO'),  # overflow
            And(name=f'FC'),  # carry
            And(name=f'FS'),  # sign
            And(name=f'FP'),  # parity
            And(name=f'FT'),  # trap
        ])
        self.flags_input = Bus([And(name=f'{name} {g.name} input') for g in self.flags])
        Register(bit_count=len(self.flags),
                 ri=And(inputs=[self.control_word[7], clock], name=f'{name} Flags Register IE'), ro=High(),
                 ibus=self.flags_input, obus=self.flags,
                 name=f'{name} Flags Register'
                 )
        control_halt_pulse = EdgeDetector(signal=self.control_word[0], sustain=5, name=f'{name} HALT Pulse')
        self.run_flag = Not(
            inputs=[DLatch(
                enable=Or(inputs=[control_halt_pulse, init_signal_pulse], name=f'{name} Halt Latch EN Sync'),
                data=Or(inputs=[control_halt_pulse], name=f'{name} Halt Latch D Sync'),
                name=f'{name} Halt Latch').output],
            name=f'Main Control Unit Run Flag')

        # ir and machine code
        iro = Bus(bit_count=16, name=f'{name} Instruction Register Output')
        # should probably use multiplexer subclass
        self.ir = Register(bit_count=16,
                           ri=And(inputs=[self.control_word[5], clock], name=f'{name} Instruction Register OE'),
                           ro=High(),
                           ibus=main_bus, obus=iro,
                           name=f'{name} Instruction Register')
        ir_param_output = BSB(b=iro[:12], oe=self.control_word[6], name=f'{name} Instruction Register Param Output')
        main_bus.connect_inputs(ir_param_output)

        # counters
        next_instruction = And(inputs=[self.control_word[4], clock], name=f'{name} Next Instruction')
        pix_in_conditional = And(inputs=[self.control_word[3], self.flags[0]])
        pix_in = Or(inputs=[self.control_word[2], pix_in_conditional])
        self.pix = CounterPlus(signal=next_instruction, reset=Low(),
                               load=And(inputs=[clock, pix_in], name=f'{name} PIX Load'),
                               d=Bus(main_bus[:8], name=f'{name} PIX sub-bus'),
                               name=f'{name} Program Instruction Index')
        Register(bit_count=8, ri=clock_, ro=self.control_word[1],
                 ibus=self.pix.outputs, obus=Bus(main_bus[:8]),
                 name=f'{name} PIX Bus Out')
        self.mix = Counter(signal=clock, bit_count=3, reset=mix_reset, name=f'{name} MicroInstruction Index')


        # microinstruction resolver
        mmi_address_space = len(self.mix.outputs)+len(iro)-len(ir_param_output)
        self.mmi = Bus(bit_count=mmi_address_space, name=f'{name} MicroInstruction Map Input')
        # micromap(opcode, mix) -> control word
        self.mmi.connect_inputs([*self.mix.outputs, *iro[-4:]])
        self.mm = TruthTable(data_input=self.mmi,
                             table=Control.MACHINE_CODE_TABLE,
                             name=f'{name} MicroInstruction Map TruthTable')
        for i, output in enumerate(self.mm.outputs):
            self.control_word_setup[i].connect_inputs([output])

    @property
    def monitor(self):
        return f'{self.control_word.monitor_named_true}' \
               f'\nFL: {self.flags.monitor_named}' \
               f'\nMIX: {self.mix.monitor}' \
               f'\nPIX: {self.pix.monitor}' \
               f'\nMM: {self.mm.monitor}' \
               f'\nIR: {self.ir.monitor}'

    @staticmethod
    def debug_machine_code():
        print('+++ Machine code: +++')
        for i, mc in enumerate(Control.MACHINE_CODE_TABLE):
            print(f'{i:>2}: {mc}')


def example_circuit():
    switches = [Switch(name=f'S{l}') for l in 'ABCDE']
    h = High(name='1')
    l = Low(name='0')
    data = Bus([h, l, h, l, l, h, l, h, l, h, l, l, l, l, h, l])
    Gate.enable_debug()
    # Gate.enable_debug(False)
    b = BitShifter(input_bus=Bus(data),
                   # ri=switches[0],
                   sl1=switches[1],
                   sl8=switches[2],
                   sr1=switches[3],
                   sr8=switches[4],
                   name=f'Shifter')
    Gate.enable_debug(False)

    return {
        'switches': switches,
        'led_panels': {
            'sl1': b.sl1,
            'sl8': b.sl8,
            'sr1': b.sr1,
            'sr8': b.sr8,
            'smuxer': b.muxer,
            'Bit Shifter': b,
            f'Data:\n{"".join(f"{s.name: ^5}" for s in data)}': data,
            f'Control:\n{"".join(f"{s.name: ^5}" for s in switches)}': switches,
        }
    }


MACHINES = {
    'default': TuringComplete().machine,
    'example': example_circuit,
}
