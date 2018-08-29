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

print("Configuring CAN...")


dwf.FDwfDigitalCanRateSet(hdwf, c_double(1e6)) # 1MHz
dwf.FDwfDigitalCanPolaritySet(hdwf, c_int(0)) # normal
dwf.FDwfDigitalCanTxSet(hdwf, c_int(0)) # TX = DIO-0
dwf.FDwfDigitalCanRxSet(hdwf, c_int(1)) # RX = DIO-1

#                    HDWF  ID         Extended  Remote    DLC      *rgTX
dwf.FDwfDigitalCanTx(hdwf, c_int(-1), c_int(0), c_int(0), c_int(0), None) # initialize TX, drive with idle level
#                    HDWF *ID   *Exte *Remo *DLC  *rgRX  cRX      *Status 0 = no data, 1 = data received, 2 = bit stuffing error, 3 = CRC error
dwf.FDwfDigitalCanRx(hdwf, None, None, None, None, None, c_int(0), None) # initialize RX reception

time.sleep(1)

rgbTX = (c_ubyte*4)(0,1,2,3)
vID  = c_int()
fExtended  = c_int()
fRemote  = c_int()
cDLC = c_int()
vStatus  = c_int()
rgbRX = (c_ubyte*8)()

print("Sending on TX...")
#                    HDWF  ID           fExtended  fRemote   cDLC              *rgTX
dwf.FDwfDigitalCanTx(hdwf, c_int(0x3FD), c_int(0), c_int(0), c_int(len(rgbTX)), rgbTX) 

tsec = time.clock() + 10 # receive for 10 seconds
print("Receiving on RX for 10 seconds...")
while time.clock() < tsec:
    time.sleep(0.01)
    #                    HDWF *ID          *Extended        *Remote         *DLC         *rgRX   cRX                  *Status
    dwf.FDwfDigitalCanRx(hdwf, byref(vID), byref(fExtended), byref(fRemote), byref(cDLC), rgbRX, c_int(sizeof(rgbRX)), byref(vStatus)) 
    if vStatus.value != 0:
        print("RX: "+('0x{:08x}'.format(vID.value)) +" "+("Extended " if fExtended.value!=0 else "")+("Remote " if fRemote.value!=0 else "")+"DLC: "+str(cDLC.value))
        if vStatus.value == 1:
            print("no error")
        elif vStatus.value == 2:
            print("bit stuffing error")
        elif vStatus.value == 3:
            print("CRC error")
        else:
            print("error")
        if fRemote.value == 0 and cDLC.value != 0:
            print("Data: "+(" ".join("0x{:02x}".format(c) for c in rgbRX[0:cDLC.value])))

dwf.FDwfDeviceCloseAll()
