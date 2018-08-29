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

print("Configuring I2C...")

iNak = c_int()

dwf.FDwfDigitalI2cRateSet(hdwf, c_double(1e5)) # 100kHz
dwf.FDwfDigitalI2cSclSet(hdwf, c_int(0)) # SCL = DIO-0
dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(1)) # SDA = DIO-1
dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
if iNak.value == 0:
    print("I2C bus error. Check the pull-ups.")
    quit()
time.sleep(1)

rgTX = (c_ubyte*16)(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
rgRX = (c_ubyte*16)()

#                                8bit address  
dwf.FDwfDigitalI2cWrite(hdwf, c_int(0x1D<<1), rgTX, c_int(16), byref(iNak)) # write 16 bytes
time.sleep(0.1)

dwf.FDwfDigitalI2cRead(hdwf, c_int(0x1D<<1), rgRX, c_int(16), byref(iNak)) # read 16 bytes
if iNak.value != 0:
    print("NAK "+str(iNak.value))
print(list(rgRX))
time.sleep(0.1)

dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(0x1D<<1), rgTX, c_int(1), rgRX, c_int(16), byref(iNak)) # write 1 byte restart and read 16 bytes
if iNak.value != 0:
    print("NAK "+str(iNak.value))
print(list(rgRX))

dwf.FDwfDeviceCloseAll()
