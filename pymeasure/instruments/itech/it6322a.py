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
    voltage_setpoint = Channel.control(
        "APPL CH{ch}; VOLT?",
        "APPL CH{ch}; VOLT %g",
        """Control the output voltage of this channel, range depends on channel.""",
        validator=strict_range,
        values=[0, 30],
        dynamic=True,
    )

    current_setpoint = Channel.control(
        "APPL CH{ch}; CURR?",
        "APPL CH{ch}; CURR  %g",
        """Control the current limit of this channel, range depends on channel.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    voltage = Channel.measurement(
        "APPL CH{ch}; MEAS:VOLT?",
        """Measure actual voltage of this channel."""
    )

    current = Channel.measurement(
        "APPL CH{ch}; MEAS:CURR?",
        """Measure the actual current of this channel."""
    )


    power = Channel.measurement(
        "APPL CH{ch}; MEAS:POW?",
        """Measure the actual power of this channel."""
    )

    output_enabled = Channel.control(
        "APPL CH{ch}; CHAN:OUTP?", 
        "APPL CH{ch}; CHAN:OUTP %s",
        """Control whether the channel output is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    ovp_setpoint = Channel.control(
        "APPL CH{ch}; VOLT:PROT?", 
        "APPL CH{ch}; VOLT:PROT %g",
        """Control the over-voltage protection level""",
        validator=strict_range,
        values=[0, 30],
    )
    
    ocp_setpoint = Channel.control(
        "APPL CH{ch}; CURR:PROT?", 
        "APPL CH{ch}; CURR:PROT %g",
        """Control the over-current protection level""",
        validator=strict_range,
        values=[0, 3],
    )
   
    ovp_enabled = Channel.control(
        "APPL CH{ch}; VOLT:PROT:STAT?", 
        "APPL CH{ch}; VOLT:PROT:STAT %d",
        """Control the over-voltage protection on/off""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )
    
    ocp_enabled = Channel.control(
        "INST:NSEL {ch}; CURR:PROT:STAT?", "INST:NSEL {ch}; CURR:PROT:STAT %d",
        """Control the over-current protection on/off""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    ovp_tripped = Instrument.measurement(
        "INST:NSEL {ch}; VOLT:PROT:TRIP?",
        """The over-voltage protection trip status.""",
        map_values=True,
        values={True: 1, False: 0}
    )

    ocp_tripped = Instrument.measurement(
        "INST:NSEL {ch}; CURR:PROT:TRIP?",
        """Read the over-voltage protection trip status.""",
        map_values=True,
        values={True: 1, False: 0}
    )    
    
    def ovp_clear(self):
        """Clear the ovp flag and enable the output,"""
        self.write("INST:NSEL {ch}:VOLT:PROT:CLE")
            
    def ocp_clear(self):
        """Clear the ocp flag and enable the output,"""
        self.write("INST:NSEL {ch}:CURR:PROT:CLE")
            
            
class  IT6322A(SCPIMixin, Instrument):
    """ Represents the ITECH IT6332A and
    provides a high-level interface for interacting with the instrument.
    """

    ch_1 = Instrument.ChannelCreator(VoltageChannel, 1)
    ch_2 = Instrument.ChannelCreator(VoltageChannel, 2)
    ch_3 = Instrument.ChannelCreator(VoltageChannel, 3)

    def __init__(self, adapter, name="IT6322A", **kwargs):
        super().__init__(
            adapter,
            name,
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
    
    channel_select = Instrument.control (
        "INST:NSEL?", "INST:NSEL %d",
        """
        Select the channel
        """,
        get_process=lambda v: int(v)        
    )