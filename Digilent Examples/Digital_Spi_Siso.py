"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-23

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import math
import sys
import time

if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()

print("Opening first device")
#dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(3), byref(hdwf)) 

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

print("Configuring SPI...")
dwf.FDwfDigitalSpiFrequencySet(hdwf, c_double(1e3))
dwf.FDwfDigitalSpiClockSet(hdwf, c_int(1))
dwf.FDwfDigitalSpiDataSet(hdwf, c_int(0), c_int(2)) # 0 DQ0_MOSI_SISO = DIO-2
dwf.FDwfDigitalSpiModeSet(hdwf, c_int(0)) # SPI mode 
dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(1)) # 1 MSB first
#                              DIO       value: 0 low, 1 high, -1 high impedance
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high
# cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad
#                                cDQ       bits 0    data 0
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(0), c_int(0), c_int(0)) # start driving the channels
time.sleep(1)

rgbTX = (c_ubyte*10)(0,1,2,3,4,5,6,7,8,9)
rgwRX = (c_uint32*10)()
dw = c_uint32()

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 low
#                                cDQ 0     bits 16
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(0), c_int(16), c_uint(0x1234)) # write 16bits
#                                cDQ 0     bits 24
dwf.FDwfDigitalSpiReadOne(hdwf, c_int(0), c_int(24), byref(dw)) # read 24bits
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 low
#                             cDQ 0     bits 16   array  length
dwf.FDwfDigitalSpiWrite(hdwf, c_int(0), c_int(8), rgbTX, c_int(len(rgbTX))) # write from array of 8bit (byte) elements in 8 bit data lengths
dwf.FDwfDigitalSpiRead16(hdwf, c_int(0), c_int(12), rgwRX, c_int(len(rgwRX))) # read to array of 16 bit (short) elements in 12bit data lengths
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high

dwf.FDwfDeviceCloseAll()
