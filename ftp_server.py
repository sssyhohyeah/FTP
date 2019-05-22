from socket import *
from threading import Thread
import os
from time import sleep

# 全局变量
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST, PORT)
FTP = "/home/tarena/month02/concurrent/FTP/"  # FTP文件库路径


# 将客户端请求功能封装为类
class FtpServer(object):
    def __init__(self, connfd, path):
        self.connfd = connfd
        self.path = path

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send(b"Empty directory")
            return
        else:
            self.connfd.send(b"ok")
            sleep(0.1)

        fs = ""
        for file in files:
            if file[0] != "." and os.path.isfile(self.path + file):
                fs += file + "\n"
        self.connfd.send(fs.encode())

    def do_download(self, fn):
        try:
            fd = open(self.path + fn, "rb+")
        except Exception:
            self.connfd.send(b"File not found")
            return
        else:
            self.connfd.send(b"ok")
            sleep(0.1)
        # 发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b"##")  # 文件结束
                break
            self.connfd.send(data)
        fd.close()

    def do_upload(self, fn):
        if os.path.exists(self.path + fn):
            self.connfd.send(b"File already exists.")
            return
        self.connfd.send(b"ok")
        fd = open(self.path + fn, "wb+")
        # 接收文件
        while True:
            data = self.connfd.recv(1024)
            if data == b"##":
                break
            fd.write(data)
        fd.close()


# 处理客户端请求函数
def handle(c):
    cls = c.recv(1024).decode()
    FTP_PATH = FTP + cls + "/"
    ftp = FtpServer(c, FTP_PATH)
    while True:
        # 接收客户端命令类型
        data = c.recv(1024).decode()
        if not data or data[0] == "Q":
            # not data利用短路原则防止客户端断开返回空字符串导致服务器直接报错
            return
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == "D":
            file_name = data.split(" ")[-1]
            ftp.do_download(file_name)
        elif data[0] == "U":
            file_name = data.split(" ")[-1]
            ftp.do_upload(file_name)


# 网络搭建（多线程并发网络）
def main():
    # 创建套接字
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("Listen to the Port 8888...")

    # 循环等待客户端请求连接
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:
            print("Server exits")
            return
        except Exception as e:
            print(e)
            continue
        print("Connecting to client:", addr)

        # 创建线程处理请求
        client = Thread(target=handle, args=(connfd,))
        client.setDaemon(True)
        client.start()


if __name__ == "__main__":
    main()
