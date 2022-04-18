# utilities library

import arrow
import pathlib
import contextlib
import time
import copy
import traceback
import os
import sys

CONSOLE_PRINT = False
DEFAULT_DEBUG_DIRECTORY = 'turing'


def ping():
    return time.time()


def pong(ping_, ms_rounding=3):
    return round((time.time() - ping_) * 1000, ms_rounding)


@contextlib.contextmanager
def pingpong(desc='Pingpong', show=False, ms_rounding=3):
    p = ping()
    yield copy.deepcopy(p)
    elapsed = pong(p, ms_rounding)
    if show:
        print(show_pong(p, desc=desc))
    return elapsed


def show_pong(p, desc='Pingpong'):
    return f'{desc} elapsed in {pong(p)}ms'


def high_low(current):
    return 'HIGH' if current else 'LOW'


def bool2binstr(bl, lsbf=True):
    return ''.join(str(int(b)) for b in (reversed(bl) if lsbf else bl))


def binstr2bool(bs, lsbf=False):
    return [bool(int(b)) for b in (bs if lsbf else reversed(bs))]


def binstr2decimal(bs, lsbf):
    s = 0
    for i, val in enumerate(binstr2bool(bs, lsbf)):
        s += (2**i)*int(val)
    return s


def binstr2tc(bs, lsbf):
    return tc2decimal(binstr2bool(bs, lsbf), lsbf)


def decimal2tc(bit_count: int, d: int, lsbf: bool):
    step = 2**(bit_count-1)
    # d = d % (step * (-1 if d < 0 else 1)) if d != -1*step else d
    if not -1*step <= d < step:
        raise ValueError(f'Cannot represent {d} in {bit_count}-bit two\'s complement!')
    if d < 0:
        s = [True]
        d = d + step
    else:
        s = [False]

    for i in reversed(range(bit_count-1)):
        step = 2**i
        c = d // step
        if c > 0:
            d = d - step
        s.append(bool(c))
    return [*reversed(s)] if lsbf else s


def tc2decimal(bl: list, lsbf: bool):
    bo = [*bl] if lsbf else [*reversed(bl)]
    v = 0
    for i, b in enumerate(bo):
        v += int(b)*(2**i) if i < (len(bo)-1) else -int(b)*(2**i)
    return v


def bool2decimal(bl: list, lsbf: bool):
    v = 0
    for i, b in enumerate(reversed(bl) if lsbf else bl):
        v += b*(2**i)
    return v


def format_exc(e):
    s = ''
    for line in traceback.format_exception(*sys.exc_info()):
        s += str(line)+'\n'
    s += str(e)
    return s


def log_disk(log_path, message, clear=False, timestamp=False, force_print=False):
    if CONSOLE_PRINT or force_print:
        print(message)
    times = f'{log_time()} - ' if timestamp else ''
    with open(log_path, 'w' if clear else 'a') as f:
        f.write(f'{times}{message}\n')


def log_time():
    return arrow.now().format("YYYY-MM-DD HH:mm:ss.SSS")


def give_path(name=DEFAULT_DEBUG_DIRECTORY):
    # set default data directory based on OS
    if os.name == 'posix':
        directory = pathlib.Path.home() / f'.{name}'
    elif os.name == 'nt':
        directory = pathlib.Path.home() / 'AppData' / 'Local' / f'{name}'
    else:
        raise NotImplementedError(f'OS not supported yet :(')

    directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir():
        raise FileNotFoundError(f'Cannot find data directory: {directory}')

    return directory


def quit_(restart=False):
    if restart:
        print(f'Restarting...')
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        print(f'Quitting...')
        quit()
