def read():
    with open(r"C:\Users\zhang\Desktop\a.mp4","rb") as f:
        print(len(f.read()))


if __name__ == '__main__':
    read()