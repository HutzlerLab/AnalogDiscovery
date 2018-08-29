"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-24

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
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

print("Opening first device")
hdwf = c_int()
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

hzSys = c_double()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(hzSys))

# 1kHz pulse on IO pin 0
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(0), c_int(1))
# prescaler to 2kHz, SystemFrequency/1kHz/2
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(0), c_int(int(hzSys.value/1e3/2)))
# 1 tick low, 1 tick high
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(0), c_int(1), c_int(1))

# 1kHz 25% duty pulse on IO pin 1
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(1), c_int(1))
# prescaler to 4kHz SystemFrequency/1kHz/2
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(1), c_int(int(hzSys.value/1e3/4)))
# 3 ticks low, 1 tick high
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(1), c_int(3), c_int(1))

# 2kHz random on IO pin 2
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(2), c_int(1))
dwf.FDwfDigitalOutTypeSet(hdwf, c_int(2), DwfDigitalOutTypeRandom)
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(2), c_int(int(hzSys.value/2e3)))

rgdSamples = (c_byte*6)(*[0xFF,0x80,0xC0,0xE0,0xF0,0x00])
# 1kHz sample rate custom on IO pin 3
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(3), 1)
dwf.FDwfDigitalOutTypeSet(hdwf, c_int(3), DwfDigitalOutTypeCustom)
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(3), c_int(int(hzSys.value/1e3)))
dwf.FDwfDigitalOutDataSet(hdwf, c_int(3), byref(rgdSamples), c_int(6*8))

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

print("Generating output for 10 seconds...")
time.sleep(10)

dwf.FDwfDigitalOutReset(hdwf)
dwf.FDwfDeviceCloseAll()
