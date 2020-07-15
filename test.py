# import os
# import re
#
# regex = re.compile("\s+(.*[1-9]+)\s+")
# devs = os.popen("ls /dev/sd*").read()
# print("devs",devs)
# usbdevs = regex.findall(devs)
# print("usbdevs",usbdevs)
# for usbdev in usbdevs:
#     os.system("sudo umount "+usbdev)
#     if not os.path.exists("/mnt/{}".format(usbdev.split("/")[-1])):
#         os.system("sudo mkdir /mnt/{}".format(usbdev.split("/")[-1]))
#     os.system("sudo mount "+usbdev+" /mnt/{}".format(usbdev.split("/")[-1]))
print("src.jpg".split("/")[-1])