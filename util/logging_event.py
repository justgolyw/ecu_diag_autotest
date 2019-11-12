#!/usr/bin/env python
# coding=utf-8
import os
import sys

class Logger():
    def __init__(self, filename="default.log"):
        self.path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), '..')), "data")
        self.file_path = os.path.join(self.path, filename)
        self.terminal = sys.stdout
        # 每次向文件写入时定位到文件头清除文件内容后在重新写入内容
        self.log = open(self.file_path, "a")
        self.log.seek(0)
        self.log.truncate()

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

    def save_log(self):
        self.log.close()

# 使用单例模式， 只构造一个实例
logger = Logger()

if __name__ == "__main__":
    print(os.path.abspath(os.path.join(os.getcwd(), '..')))
    log = Logger()
    log.write("hello")


