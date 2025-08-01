
import logging

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range



class Fluke8808A(SCPIMixin, Instrument):
    """ Represents the compact constant temperature bath from Fluke.
    """

    def __init__(self, adapter, name="Fluke 7341", **kwargs):
        kwargs.setdefault('write_termination', '\r\n')
        kwargs.setdefault('read_termination', '\r\n')
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 9600, 'data_bits': 8, 'parity': 0, 
                  'stop_bits': 20, 'timeout' : 5000},
            **kwargs
        )
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

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
        self.read()  # expected a "=>"       
        
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
    
    value = Instrument.measurement(
        "VAL1?", 
        """
        Returns the value shown on the primary display
        """,
        check_get_errors=True
    )
    
    def check_set_errors(self):
        """Check for errors after having set a property.

        Called if :code:`check_set_errors=True` is set for that property.
        """
        self.log.debug("check_set_propery")
        try:
            reply = self.read().strip()
            self.log.debug(reply)
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []
          
    def check_get_errors(self):
        """Check for errors after having get a property.

        Called if :code:`check_get_errors=True` is set for that property.
        """
        self.log.debug('check_get_errors')
        try:
            reply = self.read()
            self.log.debug(reply)
        except Exception as exc:
            log.exception("Getting a property failed.", exc_info=exc)
            raise
        else:
            return []