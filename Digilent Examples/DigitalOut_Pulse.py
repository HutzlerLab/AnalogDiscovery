"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-24

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
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

dwf.FDwfDigitalOutRunSet(hdwf, c_double(0.001)) # 1ms run
dwf.FDwfDigitalOutRepeatSet(hdwf, c_int(1)) # once
dwf.FDwfDigitalOutIdleSet(hdwf, c_int(0), c_int(1)) # 1=DwfDigitalOutIdleLow, low when not running 
dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(0), c_int(1), c_int(0)) # initialize high on start
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(0), c_int(0), c_int(0)) # low/high count zero, no toggle during run
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(0), c_int(1))

print("Generating 1ms pulse")
dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

time.sleep(1)

dwf.FDwfDigitalOutReset(hdwf)
dwf.FDwfDeviceCloseAll()
