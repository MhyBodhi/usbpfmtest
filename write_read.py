import time
import csv
import argparse
import os
import hashlib
import subprocess

def mount():
    os.system("mount /dev/sdb1 /mnt/usb")

def test_write():
    os.system('sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"')
    os.system("dd if=/dev/zero of=/mnt/usb/largefile bs=8k count=10000 1> write.txt 2>&1")
    result = os.popen("cat write.txt |awk '{print $10$11}'|tail -n 1")
    headers = ["测试项", "次数", "值"]
    rows = [
        {"测试项": "文件写速度", "次数": 1, "值": result.read().strip()},
    ]
    with open("total.csv", "w", encoding="utf-8") as f:
        l_csv = csv.DictWriter(f, headers)
        l_csv.writeheader()
        l_csv.writerows(rows)

def  test_read():
    os.system('sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"')
    os.system("dd if=/mnt/usb/largefile of=/dev/null bs=8k 1>read.txt 2>&1")
    time.sleep(1)
    result = os.popen("cat read.txt |awk '{print $10$11}'|tail -n 1")
    headers = ["测试项","次数","值"]
    rows = [
        {"测试项": "文件读速度", "次数":1, "值": result.read().strip()},
    ]
    with open("total.csv","w",encoding="utf-8") as f:
        l_csv = csv.DictWriter(f,headers)
        l_csv.writeheader()
        l_csv.writerows(rows)

def report(res,times,fail,success,percent):
    headers = ["测试项", "次数", "成功", "失败", "成功率"]
    rows = [
        {"测试项":"文件md5","次数":times,"成功":fail,"失败":success,"成功率":percent},
        {"测试项":"写速度","次数":times,"成功":fail,"失败":success,"成功率":percent},
        {"测试项":"读速度","次数":times,"成功":fail,"失败":success,"成功率":percent},
    ]
    with open("total.csv","w",encoding="utf-8") as f:
        l_csv = csv.DictWriter(f,headers)
        l_csv.writeheader()
        l_csv.writerows(rows)
        l_csv.writerow([])


def read():
    pass

def test():
    os.system("time ls")

def getFileMd5(filename):
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
def verifymd5(args):
    srcfile = args.path
    dstfile = "/mnt/usb/" + srcfile.split("/")[-1]
    os.system("cp -rf {srcfile} {dstfile}".format(srcfile=srcfile, dstfile=dstfile))
    if getFileMd5(srcfile) == getFileMd5(dstfile):
        print("测试通过...")

if __name__ == '__main__':

    parse = argparse.ArgumentParser()
    parse.add_argument("-p","--path",help="Specify U disk path...")
    args = parse.parse_args()
    verifymd5(args)
    test_write()

