import sys
sys.path.append("..")
import csv
import argparse
import re
import os
import hashlib
import logging.config
from multiprocessing import Process,Pool
import requests

logging.config.fileConfig("../log/log.conf")
logging = logging.getLogger()

class TestUsb():

    def __init__(self):

        regex = re.compile("\s+(.*[1-9]+)\s+")
        self.devs = os.popen("ls /dev/sd*").read()
        logging.info(("devs", self.devs))
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
                self.srcpath = "../resources/src." + self.url.split(r".")[-1][0:3]
                self.getFile()
            except requests.exceptions.ConnectionError:
                if os.path.exists(self.srcpath):
                    pass
                else:
                    logging.info("请检查网络连接是否正常...")
                    sys.exit()
        else:
            self.srcpath = self.url
            if os.path.exists(self.srcpath):
                pass
            else:
                logging.info("文件不存在...")
                raise FileNotFoundError
        self.dstpath =None

    def test_write_read_md5(self,usb,usbsrcpath):
        sum_read = 0
        sum_write = 0
        md5_success = 0
        times = args.times
        while times > 0:
            #测试写
            os.system('cd /mnt/{usb};rm -rf ./1g;sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=/dev/zero of=./1g bs=1k count=2048 conv=fsync 1> ~/{usb}write.txt 2>&1'.format(usb=usb))
            trans_unit = os.popen("cat ~/%swrite.txt |grep 'bytes'|awk '{print $11}'|tail -n 1" % (usb)).read().strip()
            result = float(os.popen("cat ~/%swrite.txt |grep 'bytes'|awk '{print $10}'|tail -n 1"%(usb)).read().strip())
            if trans_unit == "kB/s":
                result /= 1024
            print("结果",result)
            sum_write += result

            #测试读
            os.system('cd /mnt/{usb};sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=./1g of=/dev/null bs=1k 1>~/{usb}read.txt 2>&1'.format(usb=usb))
            trans_unit =  os.popen("cat ~/%sread.txt |grep 'bytes'|awk '{print $11}'|tail -n 1" % (usb)).read().strip()
            result = float(os.popen("cat ~/%sread.txt |grep 'bytes'|awk '{print $10}'|tail -n 1" % (usb)).read().strip())
            if trans_unit == "kB/s":
                result /= 1024
            sum_read += result

            #测试文件md5
            if self.verifymd5(usb,usbsrcpath):
                md5_success += 1

            times -= 1

        avg_write = "%.2f"%(sum_write/args.times)
        avg_read = "%.2f"%(sum_read/args.times)
        per_success = "%.2f%%"%(md5_success/args.times*100)
        headers = ["设备","测试项", "次数", "值"]
        rows = [
            {"设备":usb,"测试项": "写速度", "次数": args.times, "值": "平均"+avg_write+"MB/s"},
            {"设备":usb,"测试项": "读速度", "次数": args.times, "值": "平均"+avg_read+"MB/s"},
            {"设备":usb,"测试项": "文件md5验证", "次数": args.times, "值": "成功率"+per_success},
        ]

        with open("../reports/test{usb}.csv".format(usb=usb), "w", encoding="utf-8") as f:
            l_csv = csv.DictWriter(f, headers)
            l_csv.writeheader()
            l_csv.writerows(rows)
            e = csv.writer(f)
            e.writerow([])


    def getFileMd5(self,filename):

        if not os.path.isfile(filename):
            logging.info("文件不存在...")
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

    def totalreports(self):

        csvfiles = [file for file in os.listdir("../reports/") if file.endswith("csv")]
        try:
            with open("../total.csv", "a", newline="", encoding="utf-8") as f:
                fw_csv = csv.writer(f)
                for csvfile in csvfiles:
                    with open("../reports/"+csvfile, "r", encoding="utf-8") as fl:
                        fr_csv = csv.reader(fl)
                        for row in fr_csv:
                            fw_csv.writerow(row)
        except Exception as e:
            logging.info("生成总报告发生错误:",e)
            return

    def verifymd5(self,usb,usbsrcpath):

        os.system("sudo cp -rf {srcfile} /mnt/{usb}".format(srcfile=usbsrcpath,usb=usb))
        self.dstpath = "/mnt/{usb}/{srcfile}".format(usb=usb,srcfile=usbsrcpath.split("/")[-1])

        if self.getFileMd5(self.srcpath) == self.getFileMd5(self.dstpath):
            return True
        else:
            return False

    def run(self):
        pool = Pool(processes=10)
        for usb in self.usbs:
            usbsrcpath = "../resources/" + usb + "." + self.srcpath.split(".")[-1]
            os.system("sudo cp -rf {srcfile} {usbsrcpath}".format(srcfile=self.srcpath, usbsrcpath=usbsrcpath))
            pool.apply_async(self.test_write_read_md5,(usb,usbsrcpath))
        pool.close()
        pool.join()

    def getFile(self):
        res = requests.get(self.url).content
        with open(self.srcpath, "wb") as f:
            f.write(res)
        logging.info("下载成功...")

if __name__ == '__main__':

    try:
        for file in [file for file in os.listdir("../reports/") if file.endswith(".csv")]:
            os.remove("../reports/"+file)
        os.remove("../total.csv")
        logging.info("删除子报告...")
    except:
        logging.info("删除子报告发生了异常...")
    parse = argparse.ArgumentParser()
    parse.add_argument("-p","--path",default="https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1594816125080&di=0d9259e683840a951e07c4305adbf156&imgtype=0&src=http%3A%2F%2Fimg3.iqilu.com%2Fdata%2Fattachment%2Fforum%2F201308%2F21%2F191917yresbbyhssbbhhjb.jpg",help="Specify the transfer file path,Local path or network path...eg./home/test.jpg or https://www.baidu.com/../xxx.jpg")
    parse.add_argument("-c","--times",type=int,help="test times ...")

    args = parse.parse_args()
    if args.times == None or args.path == None:
        parse.print_help()
        sys.exit()

    usb = TestUsb()
    usb.run()
    usb.totalreports()
