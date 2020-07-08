#！/bin/bash
## 挂载U盘
mount  /dev/sdb1 /mnt/usb
## 测试写入100MB速度
sync;time sudo dd if=/dev/zero of=/var/sdcard/largefile bs=10k count=10240;time sudo sync

## 测试读取100MB速度 (清除缓存)
sync;echo 3 > /proc/sys/vm/drop_caches;time dd if=/var/sdcard/largefile of=/dev/null bs=10k