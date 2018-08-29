"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

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

iChannel = 0
hzFreq = 1000 # PWM freq Hz
prcDuty = 1.23 # duty %

hzSys = c_double()
maxDiv = c_uint()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(hzSys))
dwf.FDwfDigitalOutCounterInfo(hdwf, c_int(0), 0, byref(maxDiv))

# for low frequencies use divider as pre-scaler to satisfy counter limitation of 32k
cDiv = int(math.ceil(hzSys.value/hzFreq/maxDiv.value))
# count steps to generate the give frequency
cPulse = int(round(hzSys.value/hzFreq/cDiv))
# duty
cHigh = int(cPulse*prcDuty/100)
cLow = int(cPulse-cHigh)

print("Generate: "+str(hzSys.value/cPulse/cDiv)+"Hz duty: "+str(100.0*cHigh/cPulse)+"% divider: "+str(cDiv))

dwf.FDwfDigitalOutEnableSet(hdwf, c_int(iChannel), c_int(1))
dwf.FDwfDigitalOutTypeSet(hdwf, c_int(iChannel), c_int(0)) # DwfDigitalOutTypePulse
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(iChannel), c_int(cDiv)) # max 2147483649, for counter limitation or custom sample rate
dwf.FDwfDigitalOutCounterSet(hdwf, c_int(iChannel), c_int(cLow), c_int(cHigh)) # max 32768

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

print("Generating output for 10 seconds...")
time.sleep(10)

dwf.FDwfDigitalOutReset(hdwf)
dwf.FDwfDeviceCloseAll()
