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
sts = c_byte()
voltage = c_double()
current = c_double()
vmtr1 = c_double()
vmtr2 = c_double()
vmtr3 = c_double()
vmtr4 = c_double()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print("failed to open device")
    quit()

# set up analog IO channel nodes

# enable fixed supply supply
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(True)) 
# set voltage 3.3V or 5V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3)) 

# enable positive supply
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(0), c_double(True)) 
# set voltage between 0 and 9V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(1), c_double(6.0)) 
# set current limitation 0 and 1.5A
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(1), c_int(2), c_double(0.5)) 

# enable negative supply
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(2), c_int(0), c_double(True)) 
# set voltage between 0 and -9V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(2), c_int(1), c_double(-6.0)) 
# set current limitation between 0 and -1.5A
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(2), c_int(2), c_double(-0.5))

# enable voltage reference 1
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(3), c_int(0), c_double(True)) 
# set voltage between -10 and 10V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(3), c_int(1), c_double(7.0)) 

# enable voltage reference 2
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(4), c_int(0), c_double(True)) 
# set voltage between -10 and 10V
dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(4), c_int(1), c_double(-7.0)) 

# master enable
dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))

for i in range(1, 11):
    # wait between readings
    time.sleep(1)
    # fetch analogIO status from device
    if dwf.FDwfAnalogIOStatus(hdwf) == 0:
        break

    # fixed supply supply readings
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(0), c_int(1), byref(voltage))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(0), c_int(2), byref(current))
    print("VCC: " + str(round(voltage.value,3)) + "V\t" + str(round(current.value,3)) + "A")

    # positive supply supply readings
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(1), c_int(1), byref(voltage))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(1), c_int(2), byref(current))
    print("VP+: " + str(round(voltage.value,3)) + "V\t" + str(round(current.value,3)) + "A")

    # negative supply supply readings
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(2), c_int(1), byref(voltage))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(2), c_int(2), byref(current))
    print("VP-: " + str(round(voltage.value,3)) + "V\t" + str(round(current.value,3)) + "A")
    
    # voltmeter readings -15V..15V
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(5), c_int(0), byref(vmtr1, 0))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(6), c_int(0), byref(vmtr2, 1))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(7), c_int(0), byref(vmtr3, 2))
    dwf.FDwfAnalogIOChannelNodeStatus(hdwf, c_int(8), c_int(0), byref(vmtr4, 3))
    print("Vmtr1-4: " + str(round(vmtr1.value,3)) + "V\t"+ str(round(vmtr2.value,3)) + "V\t"+ str(round(vmtr3.value,3)) + "V\t"+ str(round(vmtr4.value,3)) + "V\t")


# close the device
dwf.FDwfDeviceClose(hdwf)
