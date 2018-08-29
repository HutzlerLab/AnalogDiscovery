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

hdwf = c_int()
usbVoltage = c_double()
usbCurrent = c_double()
auxVoltage = c_double()
auxCurrent = c_double()
deviceTemperature = c_double()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

print("Device temperature and USB/AUX supply voltage and current")

# 10 times, once per second
for i in range(1, 11):
    # wait between readings
    time.sleep(1)
    # fetch analog IO status from device
    if dwf.FDwfAnalogIOStatus(hdwf) == 0 :
        break;
    # get system monitor readings
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(2), c_int(0), byref(usbVoltage))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(2), c_int(1), byref(usbCurrent))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(2), c_int(2), byref(deviceTemperature))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(3), c_int(0), byref(auxVoltage))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(3), c_int(1), byref(auxCurrent))
    print("Temperature: " + str(deviceTemperature.value) + "*C")
    print("USB:\t" + str(round(usbVoltage.value,3)) + "V\t" + str(round(usbCurrent.value,3)) + "A")
    print("AUX:\t" + str(round(auxVoltage.value,3)) + "V\t" + str(round(auxCurrent.value,3)) + "A")
    
#close the device
dwf.FDwfDeviceClose(hdwf)
