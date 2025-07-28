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

from warnings import warn
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set


class Victor8045M(SCPIMixin, Instrument):
    """ Represents the Victor 8045M Multimeter and
    provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        dmm = Victor8045M("COM1")

    """
    # Below: stop_bits: 20 comes from
    # https://pyvisa.readthedocs.io/en/latest/api/constants.html#pyvisa.constants.StopBits
    def __init__(self, adapter, name="Victor 8045M", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 115200, 'data_bits': 8, 'parity': 0, 'stop_bits': 10},
            **kwargs
        )

    FUNCTIONS = {
        "DCV"        : "VOLT:DC", 
        "ACV"        : "VOLT:AC", 
        "DCI"        : "CURR:DC", 
        "ACI"        : "CURR:AC",
        "R2W"        : "RES", 
        "FREQ"       : "FREQ",
        "PERIOD"     : "PER", 
        "CONTINUITY" : "CONT", 
        "DIODE"      : "DIOD",
        "CAP"        : "CAP",
        "TEMP"       : "TEMP:RTD"
    }

    function = Instrument.setting(
        "CONF:%s",
        """Confgure the measurement function.

        Allowed values: "DCV", "ACV", "DCI", "ACI",
        "R2W", "FREQ", "PERIOD", "CONTINUITY", "DIODE", "CAP".""",
        validator=strict_discrete_set,
        values=FUNCTIONS,
        map_values=True,
    )
    
    reading = Instrument.measurement(
        "MEAS?",
        """If in dual display, return the primary and secondary values, else return the primary value"""
    )

    reading_primary = Instrument.measurement(
        "MEAS1?",
        """Return the primary value"""
    )

    reading_secondary = Instrument.measurement(
        "MEAS2?",
        """Return the secondary value"""
    )
    
    rate = Instrument.control(
        "RATE?", "RATE %s",
        """Configure the measurement rate.
        
        Allowed values: "F", "M", "S" """,
        values=["F", "M", "S"],
        validator=strict_discrete_set
    )
    
    dcv_range = Instrument.control(
        "RANGE?", "RANGE %s",
        """Configure the range of the DCV measurement.""",
        values = { 0.05:1, 0.5:2, 5:3, 50:4, 500:5, 1000:6 },
        validator=strict_discrete_set,
        map_values=True,
        get_process=lambda v : v.replace('V', '').strip()
    )