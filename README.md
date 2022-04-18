# Scuffed Turing
A (slow) simulator for "electronic circuits" consisting of basic logic gates. Includes a simple turing-complete machine loaded with a simple multiplication program. Inspired by Ben Eater's amazing [video series](https://www.youtube.com/playlist?list=PLowKtXNTBypGqImE405J2565dvjafglHU) building a computer from scratch using simple electronic components.

# Installation
`$ pip install -r requirements.txt`

To run, simply run `main.py` with python

`$ python main.py`


# Use
The default machine has a simple multiplication program loaded that takes two integer inputs and outputs their product. The following is an example of multiplying 3 and 5:
![](https://ariel.ninja/other/scuffed-turing-example.gif)

The stage of the running program is indicated by the Port OUT: 1 indicates waiting for the first number input, 2 indicates waiting for the second number input. Finally it will compute and output the result.

To input a number, you must switch the correct bits and then toggle the power switch off and back on. 0 is the "power" switch, 1-8 are the bits for input.

In the example, note how we switch inputs 1 and 2 for the number 3 and inputs 1 and 3 for the number 5. We switch input 0 to toggle "power".
