"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision: 5/11/2018

   Requires:                       
       Python 2.7, numpy
       python-dateutil, pyparsing
"""

from ctypes import *
import math
import numpy
import time
import sys

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

hdwf = c_int(0)
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()


# For a ROM logic channel the digital IO value addresses the custom buffer.
# The least significant digital channel, up to the log2 of buffer size will be the address space. 
# For 1024 buffer size 10 bits, DIO 0-9 will be used as address.
# These digital IO can be either inputs or outputs.
# The buffer containing output for each possible address value is required.

customSize = c_uint() # custom buffer size in bits
dwf.FDwfDigitalOutDataInfo(hdwf, c_int(15), byref(customSize))
rgbSamples = (c_ubyte*(int(customSize.value/8)))()
print("Custom size: "+str(customSize.value)+" Address space: "+str(int(numpy.log2(customSize.value))))

# initialize array with zero
for i in range(0, int(customSize.value/8)):
    rgbSamples[i] = 0

# Lets create a MUX logic with DIO-0 and 1 as input and DIO-2 as select.
# Parse each possible address value and set desired output for each bit combination.
for iAddress in range(0, customSize.value):
    fDio0 = (iAddress>>0)&1 # first input
    fDio1 = (iAddress>>1)&1 # second input
    fDio2 = (iAddress>>2)&1 # select
    # output 1 when (select is low and first input is high) or (select is high and second input is high):
    if (fDio2 == 0 and fDio0 == 1) or (fDio2 == 1 and fDio1 == 1) :
        rgbSamples[int(iAddress/8)] |= 1<<(iAddress%8)

for i in range(0, 3):
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(0), c_int(0)) # input

# DIO-15 will be used as output
dwf.FDwfDigitalOutEnableSet(hdwf, c_int(15), c_int(1)) # enable output
dwf.FDwfDigitalOutTypeSet(hdwf, c_int(15), c_int(3)) # DwfDigitalOutTypeROM
# The minimum input to output delay is 60ns for Analog Discovery and 80ns for Digital Discovery
dwf.FDwfDigitalOutDividerSet(hdwf, c_int(15), c_int(1)) # specifying division like 10 (100MHz/10 = 10MHz) will add 100ns more delay
dwf.FDwfDigitalOutDataSet(hdwf, c_int(15), byref(rgbSamples), c_int(customSize.value))

dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))

try: input = raw_input
except NameError: pass
input("Press enter to stop")

dwf.FDwfDigitalOutReset(hdwf);
dwf.FDwfDeviceCloseAll()
