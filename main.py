# machine module (main running module)

import custom
import basic
import logic
import argparse

TITLE = f'TMachine'
MACHINE_NAMES = [*custom.MACHINES.keys()]

if __name__ == '__main__':
    print(f'Starting up {TITLE}...')
    # parse arguments
    parser = argparse.ArgumentParser(description=str(TITLE))
    parser.add_argument('-c',
                        dest='md',
                        help='Disable monitor printing in console',
                        action='store_const',
                        const=True,
                        )
    parser.add_argument('-d',
                        dest='debug',
                        help='Unused debug flag',
                        action='store_const',
                        const=True,
                        )
    parser.add_argument('--m',
                        help=f'Choose a machine: {", ".join(f"{m}" for m in MACHINE_NAMES)} '
                             f'(default: {MACHINE_NAMES[0]})',
                        metavar='MachineName',
                        action='store',
                        type=str,
                        dest='machine',
                        default=MACHINE_NAMES[0],
                        )

    args = parser.parse_args()
    machine_args = custom.MACHINES[args.machine]()

    logic.Simulation(**machine_args).run()
