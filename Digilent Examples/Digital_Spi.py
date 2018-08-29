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
dwf.FDwfDigitalSpiDataSet(hdwf, c_int(1), c_int(3)) # 1 DQ1_MISO = DIO-3
dwf.FDwfDigitalSpiModeSet(hdwf, c_int(0))
dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(1)) # 1 MSB first
#                              DIO       value: 0 low, 1 high, -1 high impedance
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high
# cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad
#                                cDQ       bits 0    data 0
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(0), c_int(0)) # start driving the channels, clock and data
time.sleep(1)

rgbTX = (c_ubyte*10)(0,1,2,3,4,5,6,7,8,9)
rgbRX = (c_ubyte*10)()
rgdw = c_uint32()

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 low
#                                 cDQ 1     bits 8    MOSI  words     MISO words
dwf.FDwfDigitalSpiWriteRead(hdwf, c_int(1), c_int(8), rgbTX, c_int(len(rgbTX)), rgbRX, c_int(len(rgbRX))) # write to MOSI and read from MISO

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high

dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(8), c_uint(0xAB)) # write 1 byte to MOSI

dwf.FDwfDigitalSpiReadOne(hdwf, c_int(1), c_int(24), byref(rgdw)) # read 24 bits from MISO

dwf.FDwfDigitalSpiWrite(hdwf, c_int(1), c_int(8), rgbTX, c_int(len(rgbTX))) # write array of 8 bit (byte) length elements

dwf.FDwfDigitalSpiRead(hdwf, c_int(1), c_int(8), rgbRX, c_int(len(rgbRX))) # read array of 8 bit (byte) length elements

dwf.FDwfDeviceCloseAll()
