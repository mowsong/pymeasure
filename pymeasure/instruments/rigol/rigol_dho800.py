#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range

class VoltageChannel(Channel):
    vertical_division = Channel.control(
        "C{ch}:VDIV?",
        "C{ch}:VDIV %.2eV",
        "Control the vertical sensitivity of a channel in V/divisions.",
        validator=truncated_range,
        values=[2e-3, 10],
        get_process=lambda v: float(v.split(" ", 1)[-1][:-1]),
    )

    coupling = Channel.control(
        "C{ch}:CPL?",
        "C{ch}:CPL %s1M",
        "Control the channel coupling mode.(DC or AC)",
        validator=truncated_discrete_set,
        values={"DC": "D", "AC": "A"},
        map_values=True,
        get_process=lambda v: v.split(" ", 1)[-1][0],
    )
    
        
class RigolDHO800(SCPIMixin, Instrument):
    """ Represents the Rigol DHO800 Oscilloscope and
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        dmm = RigolDHO800("GPIB::1")

    """
    # Below: stop_bits: 20 comes from
    # https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.StopBits
    def __init__(self, adapter, name="Rigol DHO800", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        
    channel_1 = Instrument.ChannelCreator(VoltageChannel, "1")
    channel_2 = Instrument.ChannelCreator(VoltageChannel, "2")

    timebase = Instrument.control(
        ":TIMEBASE:MAIN:SCALE?",
        ":TIMEBASE:MAIN:SCALE %.2e",
        "Control the time division to the closest possible value, rounding downwards, in seconds.",
    )
    