# Simulated functions written as generators to closer replicate the description in Verilog

import numpy as np
from numba import jit, typed

import pkg_resources
__requires__ = "numpy==1.24"  # For numba
pkg_resources.require(__requires__)


def make_typed(inner):
    """Wrapper to change first arg `x_all` to a numba.typed.List for speedup and avoid deprecation warning"""
    def outer(*args, **kwargs):
        x_all_typed = typed.List(args[0])
        return inner(x_all_typed, *args[1:], **kwargs)
        # return inner(*args, **kwargs)
    return outer


@jit(nopython=True)
# @make_typed
def lp_filter(x_all, DECAY_FULL_POWER=10, DECAY_PART=900):
    """ Low-pass IIR filter simulation of Verilog implementation
    Write as a generator to simulate verilog functionality
    Default DECAY_FULL_POWER = 10 so that DECAY_FULL = 1024
    Cannot parallelise
    """
    a = (2 ** DECAY_FULL_POWER) - DECAY_PART
    b = DECAY_PART

    last_y = 0

    for x in x_all:  # always @ (posedge clk)
        y = (a * x) + (b * last_y)
        y = y >> DECAY_FULL_POWER  # Arithmetic shift to divide by DECAY_FULL
        last_y = y
        yield y


@jit(nopython=True, parallel=True)
# @make_typed
def cfd(x_all, inv_frac=3, delay_samples=100):
    """Simulation of the constant fraction discriminator (CFD) described in Verilog.
    As normally described, the parameters are `fraction` and `delay`.
    The parameter `inv_frac` is `1/fraction`, so can multiply the conjugate variable
        rather than divide (which is easier to synthesise).
    The parameter `delay_samples` is `delay * sample_rate`.
    """
    buffer = np.zeros(delay_samples)  # In effect delays the input

    for x in x_all:  # Simulate `always @ (posedge clk)`
        # Buffer update and shift
        for i in range(delay_samples - 2, 0 - 1, -1):
            buffer[i + 1] = buffer[i]
        buffer[0] = x

        # CFD calculation
        working = buffer[delay_samples - 1]  # Delay
        working = - working * inv_frac  # Negate and augment (equivalent to attenuating x)
        y = x + working
        yield y


@jit(nopython=True, parallel=True)
# @make_typed
def zero_detector(x_all):
    sign = 0
    for x in x_all:  # Simulate `always @ (posedge clk)`
        # Two's complement: MSB is 0 for non-negatives (including 0), and 1 for negatives
        last_sign = sign
        sign = 0 if x >= 0 else 1
        # In Verilog would be a continuous assignment `assign y = sign ^ last_sign` declared at the beginning
        y = sign ^ last_sign
        yield y


@jit(nopython=True)
# @make_typed
def zero_detector2(x_all):
    """A variation of `zero_detector()` that only detects rising edges of zero crossings.
    NB: using two's complement, so MSB is 0 for non-negatives (including 0), and 1 for negatives
    Cannot parallelise
    """
    sign = 0
    for x in x_all:  # Simulate `always @ (posedge clk)`
        last_sign = sign
        # In Verilog would be a continuous assignment `assign y = ???` declared at the beginning
        sign = 0 if x >= 0 else 1
        y = sign & ~last_sign  # NB using two's complement, so need -ve & +ve i.e. 1 & 0
        yield y
