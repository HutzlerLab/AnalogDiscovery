"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-24

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
import sys
import time

if sys.platform.startswith("win"):
    dwf = cdll.dwf
    dmgr = cdll.dmgr
    ftd = windll.ftd2xx
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    dmgr = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/Frameworks/libdmgr.dylib")
    ftd = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/Frameworks/libftd2xx.dylib")
else:
    dwf = cdll.LoadLibrary("libdwf.so")
    dmgr = cdll.LoadLibrary("libdmgr.so")
    ftd = cdll.LoadLibrary("libftd2xx.so")

version = create_string_buffer(32)
cDev = c_int();
dvc = (c_char*1024)()
pdid = c_int()
flags = c_int()
locid = c_int()
type = c_int()

name = create_string_buffer(64)
sn = create_string_buffer(64)

print("")
ftd.FT_GetLibraryVersion(byref(pdid))
print("FTDI Version: "+hex(pdid.value))

if ftd.FT_CreateDeviceInfoList(byref(cDev)) != 0 :
    print("FT_CreateDeviceInfoList failed")
    quit()

print("Devices: "+str(cDev.value))

for i in range(cDev.value):
    if ftd.FT_GetDeviceInfoDetail(c_int(i), byref(flags), byref(type), byref(pdid), byref(locid), sn, name, None) != 0 :
        print("Failed FT_GetDeviceInfoDetail")
    print(" "+str(i+1)+". SN:"+str(sn.value)+" "+str(name.value)+""+" flags: "+hex(flags.value)+" type: "+hex(type.value)+" id: "+hex(pdid.value)+" locid: "+hex(locid.value))


print("")
dmgr.DmgrGetVersion(version)
print("DMGR Version: "+str(version.value))

if dmgr.DmgrEnumDevices(byref(cDev)) == 0 :
    print("DmgrEnumDevices failed")
    quit()

print("Devices: "+str(cDev.value))

for i in range(cDev.value):
    dmgr.DmgrGetDvc(c_int(i), dvc);

    if dmgr.DmgrGetInfo(dvc, 3, name) == 0 : #dinfoProdName
        print("Failed DmgrGetInfo dinfoProdName")
    if dmgr.DmgrGetInfo(dvc, 4, byref(pdid)) == 0 : #dinfoPDID
        print("Failed DmgrGetInfo dinfoPDID")
    if dmgr.DmgrGetInfo(dvc, 5, sn) == 0 : #dinfoSN
        print("Failed DmgrGetInfo dinfoSN")
    print(" "+str(i+1)+". "+str(sn.value)+" "+str(name.value)+""+" PDID: "+hex(pdid.value))


print("")
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

if dwf.FDwfEnum(c_int(0), byref(cDev)) == 0 :
    print("DmgrEnumDevices failed")
    quit()

print("Devices: "+str(cDev.value))

for i in range(cDev.value):
    dwf.FDwfEnumDeviceName(c_int(i), name)
    dwf.FDwfEnumSN(c_int(i), sn)
    print(" "+str(i+1)+". "+str(sn.value)+" "+str(name.value)+"")

dmgr.DmgrFreeDvcEnum()
