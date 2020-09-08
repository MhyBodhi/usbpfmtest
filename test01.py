import multiprocessing
import time


def worker(d, key, value):
    d[key] = value


if __name__ == '__main__':
    mgr = multiprocessing.Manager()
    d = mgr.dict()
    jobs = [multiprocessing.Process(target=worker, args=(d, i, i * 2))
            for i in range(10)
            ]
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()

    b = {"name":True,"age":True}
    c = list(b.keys())
    print(c.remove("age"))
    print(b["a"])