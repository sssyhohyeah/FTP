from socket import *
import sys
from time import sleep


# 具体功能类
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # ok表示请求成功，否则打印请求失败的原因
        if data == "ok":
            # 接收文件列表，若要防止太大，可使用循环接收
            data = self.sockfd.recv(4096)
            print(data.decode())

        else:
            print(data)

    def do_download(self, fn):
        # 发送请求
        self.sockfd.send(("D " + fn).encode())
        data = self.sockfd.recv(128).decode()
        if data == "ok":
            fd = open(fn, "wb+")
            # 接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_upload(self, fn):
        try:
            fd = open(fn, "rb+")
        except Exception:
            print("File not found.")
            return

        fn = fn.split("/")[-1]
        self.sockfd.send(("U " + fn).encode())
        data = self.sockfd.recv(128).decode()
        if data == "ok":
            while True:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("Thank you.")


# 向服务器发起请求的函数
def request(s):
    ftp = FtpClient(s)
    while True:
        print("\n=========== 命令选项 ===========")
        print("************* list ************")
        print("*********** download **********")
        print("************ upload ***********")
        print("************* quit ************")
        print("===============================\n")

        cmd = input("Enter command:")
        if cmd.strip() == "list":
            s.send(cmd.encode())
            ftp.do_list()
        elif cmd.strip().split(" ")[0] == "download":
            file_name = cmd.split(" ")[-1]
            ftp.do_download(file_name)
        elif cmd.strip().split(" ")[0] == "upload":
            file_name = cmd.split(" ")[-1]
            ftp.do_upload(file_name)
        elif cmd.strip() == "quit":
            ftp.do_quit()
        else:
            pass


# 网络连接
def main():
    # 服务器地址
    ADDR = ("127.0.0.1", 8888)

    sockfd = socket(AF_INET, SOCK_STREAM)

    # 请求连接
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("Connecting to server failed.")
        return
    else:
        print("""
                *****************************
                    Data    File    Image
                *****************************
        """)
        cls = input("Enter file type:")
        if cls not in ["Data", "File", "Image"]:
            print("Sorry! Input type error!")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)


if __name__ == "__main__":
    main()
