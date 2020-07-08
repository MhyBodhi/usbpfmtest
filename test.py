import os
import subprocess
os.system("touch test.txt")
os.system("ls >test.txt;ping www.baidu.com -c1>>test.txt")