import usb.util
dev =  usb.core.find(idVendor= 0x05e3, idProduct= 0x0610)
if dev is None:
    raise ValueError('Device not found')
print(dev)