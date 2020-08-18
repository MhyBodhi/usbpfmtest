import logging
import os
import re
from multiprocessing import Pool
class TestUSB():
    def __init__(self):
        os.system("sudo bash ../__init__.sh &> /dev/null")
        regex = re.compile("\s+(.*[1-9]+)\s+")
        self.devs = os.popen("ls /dev/sd*").read()
        print(("devs", self.devs))
        self.usbdevs = regex.findall(self.devs)

        for usbdev in self.usbdevs:
            os.system("sudo umount " + usbdev + " &>/dev/null")
            if not os.path.exists("/mnt/{}".format(usbdev.split("/")[-1])):
                os.system("sudo mkdir /mnt/{}".format(usbdev.split("/")[-1]))
            os.system("sudo mount " + usbdev + " /mnt/{}".format(usbdev.split("/")[-1]))
        self.usbs = [usbdev.split("/")[-1] for usbdev in self.usbdevs]

    def test_read(self,usb):
        # 测试读
        print("测试%s读速度..." % usb)
        os.system('cd /mnt/{usb};sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=./1g of=/dev/null bs=1k 1>~/{usb}read.txt 2>&1'.format(usb=usb))
        trans_unit = os.popen("cat ~/%sread.txt |grep 'bytes'|awk '{print $11}'|tail -n 1" % (usb)).read().strip()
        result = float(os.popen("cat ~/%sread.txt |grep 'bytes'|awk '{print $10}'|tail -n 1" % (usb)).read().strip())
        if trans_unit == "kB/s":
            result /= 1024
        print("%s读速度%.2fMB/s" % (usb, result))

    def run(self):
        pool = Pool(processes=10)
        for usb in self.usbs:
            os.system('cd /mnt/{usb};rm -rf ./1g;sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=/dev/zero of=./1g bs=4k count=4096 conv=fsync 1> ~/{usb}write.txt 2>&1'.format(usb=usb))
        for usb in self.usbs:
            pool.apply_async(self.test_read, (usb,))
        pool.close()
        pool.join()

if __name__ == '__main__':
    usb = TestUSB()
    usb.run()