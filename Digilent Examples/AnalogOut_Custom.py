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

hzFreq = 1e4
cSamples = 4096
hdwf = c_int()
rgdSamples = (c_double*cSamples)()
channel = c_int(0)

# samples between -1 and +1
for i in range(0,len(rgdSamples)):
    rgdSamples[i] = 1.0*i/cSamples;

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
"Opening first device..."
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

print("Generating custom waveform...")
dwf.FDwfAnalogOutNodeEnableSet(hdwf, channel, AnalogOutNodeCarrier, c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel, AnalogOutNodeCarrier, funcCustom) 
dwf.FDwfAnalogOutNodeDataSet(hdwf, channel, AnalogOutNodeCarrier, rgdSamples, c_int(cSamples))
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, channel, AnalogOutNodeCarrier, c_double(hzFreq)) 
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, channel, AnalogOutNodeCarrier, c_double(2.0)) 

dwf.FDwfAnalogOutRunSet(hdwf, channel, c_double(2.0/hzFreq)) # run for 2 periods
dwf.FDwfAnalogOutWaitSet(hdwf, channel, c_double(1.0/hzFreq)) # wait one pulse time
dwf.FDwfAnalogOutRepeatSet(hdwf, channel, c_int(3)) # repeat 5 times

dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))

print("Generating waveform...")
time.sleep(5)

print("done")
dwf.FDwfAnalogOutReset(hdwf, channel)
dwf.FDwfDeviceCloseAll() 
