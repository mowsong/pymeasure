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

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

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
    
    DCV_RANGES   = { 0.05:1, 0.5:2, 5:3, 50:4, 500:5, 1000:6 }
    DCV_RANGES_R = { '50 mV': 1, '500 mV': 2, '5 V': 3, '50 V': 4, '500 V': 5, '1000 V': 6}
    
    dcv_range = Instrument.control(
        "CONF:VOLT:DC; RANGE?", "CONF:VOLT:DC; RANGE %s",
        """Configure the range of the DCV measurement.""",
        values = DCV_RANGES,
        validator=strict_discrete_set,
        map_values=True,
        get_process=lambda v : Victor8045M.DCV_RANGES_R[v.strip()]
    )
    
    ACV_RANGES   = { 0.5:1, 5:2, 50:3, 500:4, 750:5}
    ACV_RANGES_R = { '500 mV': 1, '5 V': 2, '50 V': 3, '500 V': 4, '750 V': 5}
    
    acv_range = Instrument.control(
        "RANGE?", "CONF:VOLT:AC; RANGE %s",
        """Configure the range of the ACV measurement.""",
        values = ACV_RANGES,
        validator=strict_discrete_set,
        map_values=True,
        get_process=lambda v : Victor8045M.ACV_RANGES_R[v.strip()]
    )