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
dwf.FDwfDigitalSpiDataSet(hdwf, c_int(2), c_int(4)) # 2 DQ2 = DIO-4
dwf.FDwfDigitalSpiDataSet(hdwf, c_int(3), c_int(5)) # 3 DQ3 = DIO-5
dwf.FDwfDigitalSpiModeSet(hdwf, c_int(0)) # SPI mode 
dwf.FDwfDigitalSpiOrderSet(hdwf, c_int(1)) # 1 MSB first
#                              DIO       value: 0 low, 1 high, -1 high impedance
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high
# cDQ 0 SISO, 1 MOSI/MISO, 2 dual, 4 quad, // 1-32 bits / word
#                                cDQ       bits     data
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(4), c_int(0), c_int(0)) # start driving the channels
time.sleep(1)

rgbCmd = (c_ubyte*2)(0xAB,0xCB)
rgdwTX = (c_uint32*16)(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
rgbRX = (c_ubyte*8)()

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 low
dwf.FDwfDigitalSpiWriteOne(hdwf, c_int(1), c_int(8), c_int(0x1D)) # write 8 bits to DQ0_MOSI
#                               cDQ quad  bits 8    data 0
dwf.FDwfDigitalSpiWrite32(hdwf, c_int(4), c_int(24), rgdwTX, c_int(len(rgdwTX))) # write from array of 32bit(int) elements in quad mode 24bit data lengths
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high

dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(0)) # CS DIO-0 low
dwf.FDwfDigitalSpiWrite(hdwf, c_int(1), c_int(8), rgbCmd, c_int(len(rgbCmd))) # write 2 bytes to MOSI
dwf.FDwfDigitalSpiRead(hdwf, c_int(4), c_int(8), rgbRX, c_int(len(rgbRX)))  # read to array of 8bit(byte) elements in dual mode 8bit data lengths
dwf.FDwfDigitalSpiSelect(hdwf, c_int(0), c_int(1)) # CS DIO-0 high

dwf.FDwfDeviceCloseAll()
