"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
dwRead = c_uint32()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

# enable output/mask on 8 LSB IO pins, from DIO 0 to 7
dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x00FF)) 
# set value on enabled IO pins
dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x12)) 
# fetch digital IO information from the device 
dwf.FDwfDigitalIOStatus (hdwf) 
# read state of all pins, regardless of output enable
dwf.FDwfDigitalIOInputStatus(hdwf, byref(dwRead)) 

#print(dwRead as bitfield (32 digits, removing 0b at the front)
print("Digital IO Pins: ", bin(dwRead.value)[2:].zfill(16))

dwf.FDwfDeviceClose(hdwf)



