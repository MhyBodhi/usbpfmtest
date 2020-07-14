import sys
import time
import csv
import argparse
import os
import hashlib


def test_write():
    try:
        os.remove("./1g")
    except:
        pass

    os.system('cd /media/kylin/*;sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches;dd if=/dev/zero of=./1g bs=1M count=1024 1> ~/write.txt 2>&1"')
    result = os.popen("cat ~/write.txt |awk '{print $10$11}'|tail -n 1")
    headers = ["测试项", "次数", "值"]
    rows = [
        {"测试项": "文件写速度", "次数": 1, "值": result.read().strip()},
    ]
    with open("write.csv", "w", encoding="utf-8") as f:
        l_csv = csv.DictWriter(f, headers)
        l_csv.writeheader()
        l_csv.writerows(rows)

def  test_read():
    os.system('cd /media/kylin/*;sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches";dd if=./1g bs=1M | dd of=/dev/null 1>~/read.txt 2>&1')
    result = os.popen("cat ~/read.txt |awk '{print $10$11}'|tail -n 1")
    headers = ["测试项", "次数", "值"]
    rows = [
        {"测试项": "文件读速度", "次数":1, "值": result.read().strip()},
    ]
    with open("read.csv", "w", encoding="utf-8") as f:
        l_csv = csv.DictWriter(f, headers)
        l_csv.writeheader()
        l_csv.writerows(rows)


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

def totalreport():
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
def verifymd5(args):
    srcfile = args.path
    dstfile = "/mnt/usb/" + srcfile.split("/")[-1]
    os.system("cp -rf {srcfile} {dstfile}".format(srcfile=srcfile, dstfile=dstfile))
    if getFileMd5(srcfile) == getFileMd5(dstfile):
        print("测试通过...")

if __name__ == '__main__':
    try:
        for file in [file for file in os.listdir(".") if file.endswith(".csv")]:
            os.remove(file)
    except:
        pass
    # parse = argparse.ArgumentParser()
    # parse.add_argument("-p","--path",help="Specify U disk path...")
    # args = parse.parse_args()
    # if args.path == None:
    #     parse.print_help()
    #     sys.exit()
    # verifymd5(args)
    test_write()
    test_read()
    totalreport()

