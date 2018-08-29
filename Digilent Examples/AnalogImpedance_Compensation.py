"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-29

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

hdwf = c_int()
szerr = create_string_buffer(512)
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()

sts = c_byte()
frequecy = 1e5
reference = 1e5

print("Reference: "+str(reference)+" Ohm  Frequency: "+str(frequecy/1e3)+" kHz for picofarad capacitors")
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) # 0 = W1-C1-DUT-C2-R-GND, 1 = W1-C1-R-C2-DUT-GND, 8 = AD IA adapter
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference)) # reference resistor value in Ohms
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(frequecy)) # frequency in Hertz
dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1))
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1)) # start
time.sleep(2)

if True:
    # open compensation is important for high frequency or high resistor values
    print("Leave the inputs open to perform open compensation.")
    try: input = raw_input
    except NameError: pass
    input("Press enter to continue.")
    dwf.FDwfAnalogImpedanceCompReset(hdwf)
    dwf.FDwfAnalogImpedanceStatus(hdwf, None) # ignore last capture, force a new one
    # do averaging of multiple measurements
    openResistance = 0
    openReactance = 0
    for i in range(10):
        while True:
            dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts))
            if sts.value == 2:
                break
        v1 = c_double()
        v2 = c_double()
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(v1))
        dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(v2))
        openResistance += v1.value/10
        openReactance += v2.value/10

    dwf.FDwfAnalogImpedanceCompSet(hdwf, c_double(openResistance), c_double(openReactance), c_double(0), c_double(0)) # apply open compensation
 
input("Connect the load and press enter to continue.")
dwf.FDwfAnalogImpedanceStatus(hdwf, None) # ignore last capture, force a new one
for i in range(10):
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
            dwf.FDwfGetLastErrorMsg(szerr)
            print(str(szerr.value))
            quit()
        if sts.value == 2:
            break
    capacitance = c_double()
    resistance = c_double()
    reactance = c_double()
    phase = c_double()
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceSeriesCapactance, byref(capacitance))
    print(str(i)+" Resistance: "+str(resistance.value)+" Ohm  Reactance: "+str(reactance.value/1e3)+" kOhm  Capacitance: "+str(capacitance.value*1e12)+" pF")
    gain0 = c_double()
    gain = c_double()
    phase = c_double()
    dwf.FDwfAnalogImpedanceStatusInput(hdwf, c_int(0), byref(gain0), None)
    dwf.FDwfAnalogImpedanceStatusInput(hdwf, c_int(1), byref(gain), byref(phase))
    print(" AWG/C1: "+str(gain0.value)+" C1/C2: "+str(gain.value)+" phase: "+str(phase.value/math.pi*180))
      
    time.sleep(0.2)

dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0)) # stop
dwf.FDwfDeviceClose(hdwf)
