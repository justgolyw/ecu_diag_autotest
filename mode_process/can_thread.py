#!/usr/bin/env python
# -*- coding:utf-8 -*-

from threading import Thread, Event
import time

class CanThread(Thread):

    def __init__(self, pcan, json_msg):
        super().__init__()
        self.__flag = Event()           # 用于暂停线程的标识
        self.__flag.set()               # 设置为True
        self.__running = Event()        # 用于停止线程的标识
        self.__running.set()            # 将running设置为True

        self.pcan = pcan
        self.json_msg = json_msg

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            self.pcan.write_request_messages(self.json_msg[:-1])
            time.sleep(self.json_msg[-1])

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()  # 设置为False
