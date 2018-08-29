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

print("Configuring UART...")

cRX = c_int(0)
fParity = c_int(0)

# configure the I2C/TWI, default settings
dwf.FDwfDigitalUartRateSet(hdwf, c_double(9600)) # 9.6kHz
dwf.FDwfDigitalUartTxSet(hdwf, c_int(0)) # TX = DIO-0
dwf.FDwfDigitalUartRxSet(hdwf, c_int(1)) # RX = DIO-1
dwf.FDwfDigitalUartBitsSet(hdwf, c_int(8)) # 8 bits
dwf.FDwfDigitalUartParitySet(hdwf, c_int(0)) # 0 none, 1 odd, 2 even
dwf.FDwfDigitalUartStopSet(hdwf, c_double(1)) # 1 bit stop length

dwf.FDwfDigitalUartTx(hdwf, None, c_int(0))# initialize TX, drive with idle level
dwf.FDwfDigitalUartRx(hdwf, None, c_int(0), byref(cRX), byref(fParity))# initialize RX reception
time.sleep(1)

rgTX = create_string_buffer(b'Hello\r\n')
rgRX = create_string_buffer(101)

print("Sending on TX for 10 seconds...")
dwf.FDwfDigitalUartTx(hdwf, rgTX, c_int(sizeof(rgTX)-1)) # send text, trim zero ending

tsec = time.clock() + 10 # receive for 10 seconds
print("Receiving on RX...")
while time.clock() < tsec:
    time.sleep(0.01)
    dwf.FDwfDigitalUartRx(hdwf, rgRX, c_int(sizeof(rgRX)-1), byref(cRX), byref(fParity)) # read up to 1024 chars
    if cRX.value > 0:
        #rgRX[cRX.value] = 0 # add zero ending to print(it properly
        print(str(rgRX.value))

dwf.FDwfDeviceCloseAll()
