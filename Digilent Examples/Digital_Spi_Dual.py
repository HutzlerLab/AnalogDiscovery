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

dwf.FDwfParamSet(c_int(1), c_int(1)) # DwfParamKeepOnClose, to keep the SPI lines driving after software connection

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
dwf.FDwfDigitalSpiFrequencySet(hdwf, c_double(1e4))
dwf.FDwfDigitalSpiClockSet(hdwf, c_int(1))
dwf.FDwfDigitalSpiDataSet(hdwf, c_int(0), c_int(2)) # 0 DQ0_MOSI_SISO = DIO-2
dwf.FDwfDigitalSpiDataSet(hdwf, c_int(1), c_int(3)) # 1 DQ1_MISO = DIO-3
dwf.FDwfDigitalSpiModeSet(hdwf, c_int(0)) # SPI mode 
dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(1)) # 1 MSB first
#                              DIO       value: 0 low, 1 high, -1 high impedance
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1))
# cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad
#                                cDQ dual  bits 0    data 0
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(2), c_int(0), c_int(0)) # start driving the channels, clock and data
time.sleep(1)

rgCmd = (c_ubyte*2)(0xAB,0xCB)
rgbTX = (c_ubyte*16)(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
rgwRX = (c_uint16*8)()

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 level 0
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(12), c_int(0x12D)) # write 12 bits of command to DQ0_MOSI, in single mode
#                             cDQ dual  bits 8    data 0
dwf.FDwfDigitalSpiWrite(hdwf, c_int(2), c_int(8), rgbTX, c_int(len(rgbTX))) # write from array of 8bit(byte) elements in dual mode 8bit data lengths
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 level 1

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 level 0
dwf.FDwfDigitalSpiWrite(hdwf, c_int(1), c_int(8), rgCmd, c_int(2)) # write to MOSI array of data with 8bit lengths, in single mode
dwf.FDwfDigitalSpiRead16(hdwf, c_int(2), c_int(12), rgwRX, c_int(len(rgwRX)))  # read to array of 16bit(short) elements in dual mode 12bit data lengths
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 level 1

dwf.FDwfDeviceCloseAll()
