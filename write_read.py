import sys
import csv
import argparse
import re
import os
import hashlib
from multiprocessing import Process
import requests

class TestUsb():

    def __init__(self):

        regex = re.compile("\s+(.*[1-9]+)\s+")
        self.devs = os.popen("ls /dev/sd*").read()
        print("devs", self.devs)
        self.usbdevs = regex.findall(self.devs)

        for usbdev in self.usbdevs:
            os.system("sudo umount " + usbdev)
            if not os.path.exists("/mnt/{}".format(usbdev.split("/")[-1])):
                os.system("sudo mkdir /mnt/{}".format(usbdev.split("/")[-1]))
            os.system("sudo mount " + usbdev + " /mnt/{}".format(usbdev.split("/")[-1]))
        self.usbs = [usbdev.split("/")[-1] for usbdev in self.usbdevs]

        # 下载jpg的url路径
        self.url = args.path.strip()

        if self.url.startswith("http"):
            try:
                self.srcpath = "src." + self.url.split(".")[-1][0:3]
                self.getFile()
            except requests.exceptions.ConnectionError:
                if os.path.exists(self.srcpath):
                    pass
                else:
                    print("请检查网络连接是否正常...")
                    sys.exit()
        else:
            if os.path.exists(self.srcpath):
                pass
            else:
                print("文件不存在...")
                raise FileNotFoundError
        self.dstpath =None

    def test_write(self,usb):
        sum = 0
        md5_success = 0
        times = args.times
        while times > 0:
            os.system('cd /mnt/{usb};rm -rf ./1g;sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=/dev/zero of=./1g bs=1k count=2048 conv=fsync 1> ~/{usb}write.txt 2>&1'.format(usb=usb))
            result = os.popen("cat ~/%swrite.txt |grep 'bytes'|awk '{print $10}'|tail -n 1"%(usb))
            result = float(result.read().strip())
            sum += result
            if self.verifymd5(usb):
                md5_success += 1
            times -= 1
        avg = "%.2f"%(sum/args.times)
        per_success = "%.2f"%(md5_success/args.times)
        headers = ["设备","测试项", "次数", "值"]
        rows = [
            {"设备":usb,"测试项": "文件写速度", "次数": args.times, "值": avg+"MB/s"},
            {"设备":usb,"测试项": "文件md5验证", "次数": args.times, "值": "成功率"+per_success},
        ]
        with open("{usb}write.csv".format(usb=usb), "w", encoding="utf-8") as f:
            l_csv = csv.DictWriter(f, headers)
            l_csv.writeheader()
            l_csv.writerows(rows)


    def test_read(self,usb):

        times = args.times
        sum = 0
        while times > 0:
            os.system('cd /mnt/{usb};sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=./1g of=/dev/null bs=1k 1>~/{usb}read.txt 2>&1'.format(usb=usb))
            result = os.popen("cat ~/%sread.txt |grep 'bytes'|awk '{print $10}'|tail -n 1"%(usb))
            sum +=  float(result.read().strip())
            times -= 1
        avg = "%.2f"%(sum/args.times)
        headers = ["设备","测试项", "次数", "值"]

        rows = [
            {"设备":usb,"测试项": "文件读速度", "次数":args.times, "值": str(avg)+"MB/s"},
        ]
        with open("{usb}read.csv".format(usb=usb), "w", encoding="utf-8") as f:
            l_csv = csv.DictWriter(f, headers)
            l_csv.writeheader()
            l_csv.writerows(rows)


    def getFileMd5(self,filename):

        if not os.path.isfile(filename):
            print("文件不存在...")
            return
        myHash = hashlib.md5()
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myHash.update(b)
        f.close()
        return myHash.hexdigest()

    def totalreport(self):

        csvfiles = [file for file in os.listdir(".") if file.endswith("csv")]
        try:
            with open("total.csv", "a", newline="", encoding="utf-8") as f:
                fw_csv = csv.writer(f)
                for csvfile in csvfiles:
                    with open(csvfile, "r", encoding="utf-8") as fl:
                        fr_csv = csv.reader(fl)
                        for row in fr_csv:
                            fw_csv.writerow(row)
        except Exception as e:
            print("生成总报告发生错误:",e)
            return

    def verifymd5(self,usb):

        os.system("sudo cp -rf {srcfile} /mnt/{usb}".format(srcfile=self.srcpath,usb=usb))
        self.dstpath = "/mnt/{usb}/{srcfile}".format(usb=usb,srcfile=self.srcpath)
        if self.getFileMd5(self.srcpath) == self.getFileMd5(self.dstpath):
            return True
        else:
            return False

    def run(self):
        usblist = []
        for usb in self.usbs:
            usblist.append(Process(target=self.test_write,args=(usb,)))
        for i in usblist:
            i.start()
        for j in usblist:
            j.join()
        usblist.clear()
        for usb in self.usbs:
            usblist.append(Process(target=self.test_read, args=(usb,)))
        for i in usblist:
            i.start()
        for j in usblist:
            j.join()

    def getFile(self):
        res = requests.get(self.url).content
        with open(self.srcpath, "wb") as f:
            f.write(res)
        print("下载成功...")

if __name__ == '__main__':

    try:
        for file in [file for file in os.listdir(".") if file.endswith(".csv")]:
            os.remove(file)
    except:
        pass
    parse = argparse.ArgumentParser()
    parse.add_argument("-p","--path",help="Specify the transfer file path,Local path or network path...eg./home/test.jpg or https://www.baidu.com/../xxx.jpg")
    parse.add_argument("-c","--times",type=int,help="test times ...")
    # parse.add_argument("-w","--write",action="store_true",default=False,help="test write ...")
    # parse.add_argument("-r","--read",action="store_true",default=False,help="test read ...")
    args = parse.parse_args()
    if args.times == None or args.path == None:
        parse.print_help()
        sys.exit()

    # if args.write and args.read:
    #     test_write()
    #     test_read()
    # elif args.write:
    #     test_write()
    # elif args.read:
    #     test_read()
    # else:
    #     parse.print_help()
    #     sys.exit()
    usb = TestUsb()
    usb.run()
    usb.totalreport()
