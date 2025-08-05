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
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range, strict_discrete_set

class VoltageChannel(Channel):
    
    bwlimit = Channel.control(
        ":CHAN{ch}:BWL?", ":CHAN{ch}:BWL %s",
        """Control the 20MHz bandwidth limit of a channel.""",
        validator=strict_discrete_set,
        values = ["20M", "OFF"]
    )
    
    coupling = Channel.control(
        "CHAN{ch}:COUP?", "CHAN{ch}:COUP %s",
        """Control the channel coupling mode.""",
        validator=strict_discrete_set,
        values={"DC", "AC", "GND"},
    )
    
    display = Channel.control(
        "CHAN{ch}:DISP?", "CHAN{ch}:DISP %d",
        """Control the channel on/off.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )
    
    offset = Channel.control(
        "CHAN{ch}:OFFS?", "CHAN{ch}:OFFS %.2e",
        "Control the vertical offset of a channel in V.",
    )

    invert = Channel.control(
        "CHAN{ch}:INV?", "CHAN{ch}:INV %d",
        """Control the channel inversion.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )

    scale = Channel.control(
        "CHAN{ch}:SCAL?", "CHAN{ch}:SCAL %.2e",
        "Control the vertical scale of a channel in V/div.",
        validator=truncated_range,
        values=[500e-6, 10]
    )

    attenuation = Channel.control(
        "CHAN{ch}:PROB?", "CHAN{ch}:PROB %s",
        "Control the probe ratio a channel.",
        validator=strict_discrete_set,
        values=[ (i * pow(10, base)) for base in range(-3, 5) for i in [1, 2, 5] ] + [150, 1500, 15000]
    )

    label_enabled = Channel.control(
        "CHAN{ch}:LAB:SHOW?", "CHAN{ch}:LAB:SHOW %d",
        """Control the label display of a channel.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )

    label = Channel.control(
        ":CHAN{ch}:LAB:CONT?", ":CHAN{ch}:LAB:CONT %s",
        """Control the label string of a channel.""",
    )
    
    vernier_enabled = Channel.control(
        "CHAN{ch}:VERN?", "CHAN{ch}:VERN %d",
        """Control the fine adjustment on/off of the vertical scale of a channel.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )

    # this is just the offset
    position = Channel.control(
        "CHAN{ch}:POS?", "CHAN{ch}:POS %.2e",
        "Control the vertical offset of a channel in V.",
    )


class TriggerChannel(Channel):


    trigger_level = Channel.measurement(
        "TRLV?",
        docs="""Get the current trigger level as a dict with keys:
        - "source": trigger source whose level will be changed (str, {EX,EX/5,C1,C2})
        - "level": Level at which the trigger will be set (float)

        """,
        get_process=lambda v: {
            "source": v.split(":", 1)[0],
            "level": float(v.split(" ", 1)[-1][:-2]),
        },
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

    ch_1 = Instrument.ChannelCreator(VoltageChannel, 1)    
    ch_2 = Instrument.ChannelCreator(VoltageChannel, 2)    
    ch_3 = Instrument.ChannelCreator(VoltageChannel, 3)    
    ch_4 = Instrument.ChannelCreator(VoltageChannel, 4)    
 
    def opc(self):
        self.write("*OPC")
    
    def is_opc(self):
        return self.ask("*OPC?") 
       
    def clear(self):
        """Clear all the waveforms on the screen."""
        self.write(":CLE")
        
    def run(self):
        """Starts running the oscilloscope."""
        self.write("RUN")
    
    def stop(self):
        """Stops running the oscilloscope."""
        self.write(":STOP")
    
    def single(self):
        """Perfoms a single trigger."""
        self.write(":SING") 
    
    def force_trigger(self):
        """Generates a trigger signal forcefully."""
        self.write(":TFOR")
    
    def autoset(self):
        """Enabled the waveform auto setting."""           
        self.write(":AUT")
    
    autoset_peak = Instrument.control(
        ":AUT:PEAK?", ":AUT:PEAK %d",
        """Control the peak-peak pririoty setting.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )
        
    autoset_enabled_channels_only = Instrument.control(
        ":AUT:OPEN?", ":AUT:OPEN %d",
        """Configure the test on the channels in autoset. If disabled, all the channels will be tested.
        If no signal is found on the channel, then the channel is disabled.
        If enabled, only the enabled channels will be tested.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )
        
    autoset_overlap = Instrument.control(
        ":AUT:OVER?", ":AUT:OVER %d",
        """Control waveform overlap display mode.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )

    autoset_keep_coupling = Instrument.control(
        ":AUT:KEEP?", ":AUT:KEEP %d",
        """Configure the coupling mode in autoset. When disabled, DC-coupling is used.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )

    autoset_lock = Instrument.control(
        ":AUT:LOCK?", ":AUT:LOCK %d",
        """Configure the on/off status of the AUTO function.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )

    timebase_scale = Instrument.control(
        ":TIM:SCAL?",
        ":TIM:SCAL %.2e",
        "Control the time division to the closest possible value, rounding downwards, in seconds.",
    )
    
    timebase_mode = Instrument.control(
        "TIM:MODE?", "TIM:MODE %s",
        """
        Configure the mode of the horizontal timebase.
        """,
        validator=strict_discrete_set,
        values=['MAIN', 'XY', 'ROLL']
    ) 
    
    timebase_offset = Instrument.control(
        "TIM:OFFSET?", "TIM:OFFSET %e",
        """
        Configure the timebase offset.
        """,
    )
    
    def save_screen(self, filename='ds1054z_capture.png', format='PNG'):
        self.write(f":DISP:DATA? {format}")
        raw_data = self.read_bytes(count=-1, break_on_termchar=True)
        """
        1st byte is #, the start denoter of the data stream
        # 2nd byte is N, width of the data length in the TMC header
        # For example, #9001152054; wherein N is 9 and 001152054 is the length of the effective data
        """
        header_skips = int(chr(raw_data[1])) + 2
        with open(filename, 'wb') as fout:
            fout.write(raw_data[header_skips:]) 
            
    counter_value = Instrument.measurement(
        ":COUN:CURR?",
        """Queries the measurement value of the frequency counter.""",
    )
    
    counter_enabled = Instrument.control(
        ":COUN:ENAB?", ":COUN:ENAB %d",
        """Enable the counter.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )
    
    counter_source = Instrument.control(
        ":COUN:SOUR?", ":COUN:SOUR %s",
        """Control the source of the frequency counter.""",
        validator=strict_discrete_set,
        values=["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    )
    
    counter_mode = Instrument.control(
        "COUN:MODE?", "COUN:MODE %s",
        """Control the mode of the frequency counter.""",
        validator=strict_discrete_set,
        values = ["FREQUENCY", "PERIOD", "TOTALIZE"]
    )
    
    counter_digits = Instrument.control(
        "COUN:NDIG?", "COUN:NDIG %d",
        """Control resolution of the frequency counter.""",
        validator=strict_discrete_set,
        values = [3, 4, 5, 6]
    )
    
    counter_statistics_enabled = Instrument.control(
        "COUN:TOT:ENAB?", "COUN:TOT:ENAB %d",
        """Control frequency counter.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, "on": 1, "ON": 1, False: 0, "off": 0, "OFF": 0}
    )
    
    def counter_statistics_clear(self):
        self.write(":COUN:TOT:CLE")