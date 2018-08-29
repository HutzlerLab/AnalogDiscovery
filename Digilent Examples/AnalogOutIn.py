"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import time
from dwfconstants import *
import sys
import matplotlib.pyplot as plt
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("Version: "+str(version.value))

cdevices = c_int()
dwf.FDwfEnum(c_int(0), byref(cdevices))
print("Number of Devices: "+str(cdevices.value))

if cdevices.value == 0:
    print("no device detected")
    quit()

print("Opening first device")
hdwf = c_int()
dwf.FDwfDeviceOpen(c_int(0), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

print("Configure and start first analog out channel")
dwf.FDwfAnalogOutEnableSet(hdwf, c_int(0), c_int(1)) # 1 = Sine wave")
dwf.FDwfAnalogOutFunctionSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogOutFrequencySet(hdwf, c_int(0), c_double(3000))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))

print("Configure analog in")
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(1000000))
print("Set range for all channels")
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(4))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(1000))

print("Wait after first device opening the analog in offset to stabilize")
time.sleep(2)

print("Starting acquisition...")
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))

sts = c_int()
while True:
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
    if sts.value == DwfStateDone.value :
        break
    time.sleep(0.1)
print("   done")

rg = (c_double*1000)()
dwf.FDwfAnalogInStatusData(hdwf, c_int(0), rg, len(rg)) # get channel 1 data
#dwf.FDwfAnalogInStatusData(hdwf, c_int(1), rg, len(rg)) # get channel 2 data

dwf.FDwfAnalogOutReset(hdwf, c_int(0))
dwf.FDwfDeviceCloseAll()

dc = sum(rg)/len(rg)
print("DC: "+str(dc)+"V")

plt.plot(numpy.fromiter(rg, dtype = numpy.float))
plt.show()

