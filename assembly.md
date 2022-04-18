
# Assembly v1
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

# Assembly v2

#  Instruction  |  Opcode   |01 02 03 04 05 06 07 08 09 10-
#---------------|-----------|-------------------------------------
# Halt          |   00000   | Condition    |
# Set Flags     |   00001   | Condition    |
# Send          |   00010   | Source       | Sink         |
# Swap          |   00011   | Sink         | Sink         |
# RLoad         |   00100   | Sink         | ++
# RSave         |   00101   | Source       | ++
# RSwitch       |   00110   | Sink         | ++
# PLoad         |   00111   | Sink         | ++
# Jump          |   01000   | Condition    | Source       |
# Jump Link     |   01001   | Condition    | Source       |
#               |   01010   |
#               |   01011   |
#               |   01100   |
#               |   01101   |
#               |   01110   |
#               |   01111   |
#               |   10000   |
#               |   10001   |
#               |   10010   |
#               |   10011   |
#               |   10100   |
#               |   10101   |
#               |   10110   |
#               |   10111   |
#               |   11000   |
#               |   11001   |
#               |   11010   |
#               |   11011   |
#               |   11100   |
#               |   11101   |
#               |   11110   |
#               |   11111   |

### Sources
- REG: JO/KO/XO/YO
- ALU: AA/AS/AM/AD
- LOG: L&/L|/L^/L~
- SHI: L1/L8/R1/R8
- IOP: PO///

### Sinks
- REG: JI/KI/XI/YI
- IOP: PI///

### Conditions
- FLA: A/V/Z/NZ
- SIG: P/N/NP/NN


### 5-bit Parameters
00000 Par
00001 RAM
00010 ---
00011 ---
00100 Register J
00101 Register K
00110 Register X
00111 Register Y
01000 Arithmetic Add
01001 Arithmetic Sub
01010 Arithmetic Mul
01011 Arithmetic Div
01100 Logical And
01101 Logical Or
01110 Logical Xor
01111 Logical Not
10000 <<1
10001 <<8
10010 >>1
10011 >>8
10100 Port In
10101 Port Out
10110 ---
10111 ---


# FlagCond - 110
11000 Always
11001 Overflow
11010 Zero
11011 Non-Zero
# SignCond - 111
11100 Positive
11101 Negative
11110 Non-Positive
11111 Non-Negative
