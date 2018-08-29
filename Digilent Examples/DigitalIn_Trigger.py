"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()


# generate counter
for i in range(0, 8):
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(i), c_int(1))
    dwf.FDwfDigitalOutDividerSet(hdwf, c_int(i), c_int(1<<i))
    dwf.FDwfDigitalOutCounterSet(hdwf, c_int(i), c_int(1), c_int(1))

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))


#sample rate = system frequency / divider, 100MHz/1
dwf.FDwfDigitalInDividerSet(hdwf, c_int(1))
# 16bit per sample format
dwf.FDwfDigitalInSampleFormatSet(hdwf, c_int(16))
# set number of sample to acquire
cSamples = 1000
rgwSamples = (c_uint16*cSamples)()
dwf.FDwfDigitalInBufferSizeSet(hdwf, c_int(cSamples))
dwf.FDwfDigitalInTriggerSourceSet(hdwf, c_ubyte(3)) # trigsrcDetectorDigitalIn
dwf.FDwfDigitalInTriggerPositionSet(hdwf, c_int(int(cSamples/2)))
dwf.FDwfDigitalInTriggerSet(hdwf, c_int(0), c_int(0), c_int(0), c_int(1<<7)) # DIO7 falling edge

# begin acquisition
dwf.FDwfDigitalInConfigure(hdwf, c_bool(0), c_bool(1))
print("Waiting for acquisition...")

while True:
    dwf.FDwfDigitalInStatus(hdwf, c_int(1), byref(sts))
    print("Status:", str(sts.value))
    if sts.value == 2 : # done
        break
    time.sleep(1)
print("   done")

# get samples, byte size
dwf.FDwfDigitalInStatusData(hdwf, rgwSamples, 2*cSamples)
dwf.FDwfDeviceCloseAll()

plt.plot(numpy.fromiter(rgwSamples, dtype = numpy.uint16))
plt.show()


