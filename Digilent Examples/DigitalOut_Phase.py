"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
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


print("Generating on 2 pins phase 180* with different initial low and high polarity")
for i in range(0, 2):
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(i), c_int(1))
    dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(i), c_uint(i==1), c_uint(50)) 
    dwf.FDwfDigitalOutCounterSet(hdwf, c_int(i), c_uint(50), c_uint(50)) # 100MHz base freq /(50+50) = 1MHz

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))
print("   for 5 seconds...")
time.sleep(5)


print("Generating on 3 pins 3 phases with different initial counter values")
dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(0), c_uint(1), c_uint(0))
dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(1), c_uint(0), c_uint(20))
dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(2), c_uint(1), c_uint(10))
for i in range(0, 3):
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(i), c_int(1))
    dwf.FDwfDigitalOutCounterSet(hdwf, c_int(i), c_uint(30), c_uint(30)) # 100MHz base freq /(30+30) = 1.67 MHz

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))
print("   for 5 seconds...")
time.sleep(5)

print("Generating on 4 pins 4 phases with different initial counter values")
for i in range(0, 4):
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(i), c_int(1))
    dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(i), c_uint((i==2) or (i==3)), c_uint(25 if (i==0 or i==2) else 50))
    dwf.FDwfDigitalOutCounterSet(hdwf, c_int(i), c_uint(50), c_uint(50)) 

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))
print("   for 5 seconds...")
time.sleep(5)

dwf.FDwfDigitalOutReset(hdwf)
dwf.FDwfDeviceCloseAll()
