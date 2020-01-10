#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Author : yangwei.li
@Create date : 2019-10-25
@FileName : PCANBase.py
"""
import re

from device.pcan.PCANBasic import *
from util.logging_event import logger
import time
from util.invalid_exception import InvalidException



class Pcan():

    def __init__(self, bus, baud, message_filter):
        self.pcan_obj = PCANBasic()
        self.bus = bus
        self.baud = baud
        self.message_filter = message_filter
        self.init_pcan_usbbus()
        # self.pcan_obj.FilterMessages(self.bus, fromid, toid, PCAN_MODE_STANDARD)

    # 初始化pcan,获取pcan的串口状态
    def init_pcan_usbbus(self):
        result = self.pcan_obj.Initialize(self.bus, self.baud)
        if result != PCAN_ERROR_OK:
            # An error occurred, get a text describing the error and show it
            result = self.pcan_obj.GetErrorText(result)
            print(result[1])
        else:
            print("PCAN-PCAN_USBBUS1 (Ch-1) was initialized")

        result = self.pcan_obj.GetValue(self.bus, self.message_filter)
        if result[0] != PCAN_ERROR_OK:
            # An error occurred, get a text describing the error and show it
            result = self.pcan_obj.GetErrorText(result)
            print(result)
        else:
            # A text is shown giving information about the current status of the filter
            if result[1] == PCAN_FILTER_OPEN:
                print("The message filter for the PCAN-USB, channel 1, is completely opened.")
            elif result[1] == PCAN_FILTER_CLOSE:
                print("The message filter for the PCAN-USB, channel 1, is closed.")
            elif result[1] == PCAN_FILTER_CUSTOM:
                print("The message filter for the PCAN-USB, channel 1, is custom configured.")

    # reset PCANBase.py
    def reset_pcan(self):
        cur_status = self.pcan_obj.GetStatus(self.bus)
        if cur_status != PCAN_ERROR_OK:
            res_status = self.pcan_obj.Reset(self.bus)
            if res_status != PCAN_ERROR_OK:
                print('please plug the PCANBase.py by hand !')
            else:
                print("PCAN-PCAN_USBBUS1 (Ch-1) reset suc !")

    def get_pcan_msg(self, msg):
        pcan_msg = TPCANMsg()
        pcan_msg.ID = int(msg[0], 16)
        pcan_msg.MSGTYPE = PCAN_MESSAGE_STANDARD
        pcan_msg.LEN = int(msg[1])
        for i in range(0, int(msg[1])):
            pcan_msg.DATA[i] = int(msg[i+2], 16)
        return pcan_msg

    def write_request_messages(self, msg):
        pcan_msg = self.get_pcan_msg(msg)
        result = self.pcan_obj.Write(self.bus, pcan_msg)
        if result != PCAN_ERROR_OK:
            # An error occurred, get a text describing the error and show it
            result = self.pcan_obj.GetErrorText(result)
            # print(result)
            logger.write(str(result))
        else:
            # print("send message:", msg)
            logger.write("send message:" + str(msg) + "\n")


    # 读取响应消息
    def read_respond_messages(self):
        a, b, c = self.pcan_obj.Read(self.bus)
        # total_timestamp = 0
        if '0x'+hex(b.ID)[2:].rjust(4, '0') != '0x000L':     # not print the content if can_id = 0x000L
            print("Read Msg: {0}; Len: {1}; DATA:{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}".format
                             ('0x'+hex(b.ID)[2:].rjust(4, '0'), b.LEN, hex(b.DATA[0])[2:].rjust(2, '0'),
                              hex(b.DATA[1])[2:].rjust(2, '0'), hex(b.DATA[2])[2:].rjust(2, '0'),
                              hex(b.DATA[3])[2:].rjust(2, '0'), hex(b.DATA[4])[2:].rjust(2, '0'),
                              hex(b.DATA[5])[2:].rjust(2, '0'), hex(b.DATA[6])[2:].rjust(2, '0'),
                              hex(b.DATA[7])[2:].rjust(2, '0')))

        return a, b, c

    # check 响应消息
    def check_response_msg(self, check_msg_str):
        start_time = time.time() # 开始时间
        wait_flag = "(.*)L=8 037F(.{2})78"
        loop = 2000
        while loop:
            status, message, timestamp = self.pcan_obj.Read(self.bus)
            current_id = hex(message.ID)  # 响应消息ID
            str_msg = 'id=0' + current_id[2:] + ' l=8 '
            for i in range(0, 8):
                str_msg += hex(message.DATA[i])[2:].rjust(2, '0')
            str_msg = str_msg.upper()
            if current_id != hex(0):
                if status == PCAN_ERROR_OK :
                    # print('response message:', str_msg)
                    if "ID=07A9" in str_msg:
                        logger.write('response message:' + str_msg + "\n")
                        match_group = re.match(check_msg_str.upper(), str_msg)
                        if match_group:
                            # print("found ", check_msg_str)
                            logger.write("found " + check_msg_str + "\n")
                            # print(hex(message.DATA[0]))
                            return message
            else:
                time.sleep(0.002)
            flag_wait = re.match(wait_flag.upper(), str_msg.upper())
            if flag_wait:
                loop = loop + 3
            else:
                loop = loop - 1
            if time.time() - start_time > 10:
                break
        # print("not found ", check_msg_str)
        logger.write("not found " + check_msg_str + "\n")
        raise InvalidException("not receive the correct response")


if __name__ == "__main__":
    demo_can = Pcan(PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_MESSAGE_FILTER)
    # demo_can.transmit_msg(["790","8","02","3E","00","00","00","00","00","00"], "(.*)id=0798 l=8(.*)027E00")
    demo_can.write_request_messages(["7A1", "8", "02", "10", "01", "00", "00", "00", "00", "00"])
    time.sleep(0.1)
    # demo_can.read_respond_messages()
    demo_can.check_response_msg("(.*)id=07A9 l=8(.*)065001")
