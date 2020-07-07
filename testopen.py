import os
import hashlib
import argparse
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
if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("-s",help="srcfile...")
    parse.add_argument("-p",help="dstfile path...")
    args = parse.parse_args()
    srcfile = args.s.strip()
    dstpath = args.p.strip()
    os.system("cp -rf %s %s"%(srcfile,dstpath))
    if getFileMd5(srcfile) == getFileMd5(dstpath):
        print("md5 ok...")
