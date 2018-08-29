"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import time
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#declare ctype variables
hdwf = c_int()

#open device
"Opening first device..."
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

hzRate = 1e6
cSamples = 100
channel = c_int(0)
rgdSamples = (c_double*cSamples)()
# samples between -1 and +1
for i in range(0,cSamples):
    if i % 2 == 0:
        rgdSamples[i] = 0;
    else:
        rgdSamples[i] = 1.0*i/cSamples;

dwf.FDwfAnalogOutNodeEnableSet(hdwf, channel, AnalogOutNodeCarrier, c_bool(True))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, channel, AnalogOutNodeCarrier, c_double(2.0)) 
dwf.FDwfAnalogOutIdleSet(hdwf, channel, c_int(1)) # DwfAnalogOutIdleOffset

dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel, AnalogOutNodeCarrier, c_int(31)) # funcPlay
dwf.FDwfAnalogOutNodeDataSet(hdwf, channel, AnalogOutNodeCarrier, rgdSamples, cSamples)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, channel, AnalogOutNodeCarrier, c_double(hzRate)) 
dwf.FDwfAnalogOutRunSet(hdwf, channel, c_double(cSamples/hzRate)) # run for pattern duration
dwf.FDwfAnalogOutRepeatSet(hdwf, channel, c_int(1)) # repeat once

dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))

print("Generating pattern...")
time.sleep(5)

print("done")
dwf.FDwfAnalogOutReset(hdwf, channel)
dwf.FDwfDeviceCloseAll() 
