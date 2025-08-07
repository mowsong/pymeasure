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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class Fluke8808A(SCPIMixin, Instrument):
    """ Represents the compact constant temperature bath from Fluke.
    """

    def __init__(self, adapter, name="Fluke 8808A", **kwargs):
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('read_termination', '\r\n')
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 9600, 'data_bits': 8, 'parity': 0, 
                  'stop_bits': 20, 'timeout' : 5000},
            **kwargs
        )

    id = Instrument.measurement(
        "*IDN?",
        """Get the identification of the instrument.""",
        cast=str,
        maxsplit=0,
        check_get_errors=True
    )
    
    def reset(self):
        """Reset the instrument."""
        self.write("*RST")
        self.wait_for(3)
        # self.read()  # expected a "=>"  
        self.check_get_errors()     
        
    format = Instrument.control(
        "FORMAT?", "FORMAT %d",
        """
        Set output fomrat to 1 or 2
        """,
        check_set_errors=True,
        check_get_errors=True
    )
    
    function = Instrument.control(
        "FUNC1?", "%s",
        """
        Set function.
      
        OHMS, OHMS2, WIRE2, WIRE4, VAC, VAC2,
        VADCFC, VDC, VDC2
        """,
        check_set_errors=True,
        check_get_errors=True
    )
    
    reading = Instrument.measurement(
        "VAL1?", 
        """
        Returns the value shown on the primary display
        """,
        check_get_errors=True
    )
    
    def auto_ranging(self):
        """Use autoranging."""
        self.write("AUTO")
        self.wait_for(1)
        self.check_get_errors()     
    
    range = Instrument.control(
        "RANGE1?", "RANGE %s",
        """
        Stes the primary display to <value range> where <value range> is the number
        in the Range Value column of Table 4-11A
        """,
        check_get_errors=True,
        check_set_errors=True
    )
    
    rate = Instrument.control(
        "RATE?", "RATE %s",
        """
        Sets the measurement rate.
        
        Available rates are 'S', 'M', 'F'
        """,
        validator=strict_discrete_set,
        values=['S', 'M', 'F'],
        check_set_errors=True,
        check_get_errors=True
    )
    
    def check_set_errors(self):
        """Check for errors after having set a property.

        Called if :code:`check_set_errors=True` is set for that property.
        """
        logger.debug("check_set_propery")
        try:
            reply = self.read().strip()
            logger.debug(reply)
        except Exception as exc:
            logger.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []
          
    def check_get_errors(self):
        """Check for errors after having get a property.

        Called if :code:`check_get_errors=True` is set for that property.
        """
        logger.debug('check_get_errors')
        try:
            reply = self.read()
            logger.debug(reply)
        except Exception as exc:
            logger.exception("Getting a property failed.", exc_info=exc)
            raise
        else:
            return []