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

import logging

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_range, truncated_discrete_set, truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class VoltageChannel(Channel):

    voltage = Channel.measurement(
        "APPL CH{ch}; MEAS:VOLT?",
        """Measure actual voltage of this channel."""
    )

    current = Channel.measurement(
        "APPL CH{ch}; MEAS:CURR?",
        """Measure the actual current of this channel."""
    )

class  L303SP(SCPIMixin, Instrument):
    """ Represents the eTM L303SP and
    provides a high-level interface for interacting with the instrument.
    """

    def __init__(self, adapter, name="L303SP", **kwargs):
        kwargs.setdefault('write_termination', '\n')
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 9600, 'data_bits': 8, 'parity': 0, 
                  'stop_bits': 20, 'timeout' : 5000},
            **kwargs
        ) 
        
    def beep(self):
        """This command causes the multimeter to beep once."""
        self.write("SYST:BEEP")
        
    # System related commands
    remote_control_enabled = Instrument.setting(
        "SYST:%s",
        """Control whether remote control is enabled.""",
        validator=strict_discrete_set,
        values={True: "REM", False: "LOC"},
        map_values=True,
    )
    
    output_enabled = Instrument.control(
        "OUTP:STAT?",
        "OUTP:STAT %s",
        """Control whether the output is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ON', False: 'OFF'},
    )
    
    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %g",
        """Control the output voltage.""",
        validator=strict_range,
        values=[0, 30],
        dynamic=True,
    )

    current_setpoint = Instrument.control(
        "CURR?",
        "CURR %g",
        """Control the output current.""",
        validator=strict_range,
        values=[0, 3],
        dynamic=True,
    )
