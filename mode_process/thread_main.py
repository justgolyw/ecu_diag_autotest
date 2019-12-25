#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Author : yangwei.li
@Create date : 2019-10-29
@FileName : message_process.py
"""
import os, time

from device.pcan.PCANBase import *
from mode_process.data_process import DataProcess
from mode_process.security_algorithm import security_geely
from mode_process.can_thread import CanThread

class ThreadMain():

    def __init__(self, json_path, data_path):
        self.json_path = json_path
        self.data_path = data_path
        self.dataProcess = DataProcess()
        self.json_data = self.dataProcess.read_json_file(self.json_path)
        self.line_list = self.dataProcess.open_files(data_path)

        self.json_msg = self.dataProcess.get_json_msg(self.json_data, "send_message")
        self.check_messages = self.dataProcess.get_json_msg(self.json_data, "check_message")
        self.head_data = self.dataProcess.get_json_msg(self.json_data, "concat_msg,head_data")
        self.mask = eval(self.dataProcess.get_json_msg(self.json_data, "mask"))
        self.thread_msg = self.dataProcess.get_json_msg(self.json_data, "thread_msg")

    # 发送和检查消息
    def send_check_messages(self, pcan):
        driver_file_index = 0
        app_file_index = 1
        send_msg = [0, 0]
        # json_msg = self.dataProcess.get_json_msg(self.json_data, "send_message")
        # check_messages = self.dataProcess.get_json_msg(self.json_data, "check_message")
        # head_data = self.dataProcess.get_json_msg(self.json_data, "concat_msg,head_data")
        # mask = 0x1DD47818
        # mask = eval(self.dataProcess.get_json_msg(self.json_data, "mask"))

        send_msg[0] = self.head_data
        dict_thread = {}
        for key, val in dict(self.json_msg).items():
            flag = val[0] # 操作类型
            can_data = val[1]
            send_msg[1] = can_data
            delay_time = val[-1]
            # check_msg = check_messages[key] # 检查字符串
            if flag == "app_seed" or flag == "boot_seed":
                check_msg = self.check_messages[key]  # 检查字符串
                self.seed = self.security_seed(pcan, send_msg, check_msg)
            elif flag == "app_access" or flag == "boot_access":
                check_msg = self.check_messages[key]  # 检查字符串
                self.security_access(pcan, self.mask, self.seed, send_msg, check_msg, flag)
            elif flag == "FFCF":
                check_msg = self.check_messages[key]  # 检查字符串
                self.send_check_mult(pcan, send_msg, check_msg)
            elif flag == "request_driver":
                check_msg = self.check_messages[key]  # 检查字符串
                self.max_block_size = self.request_download(pcan, self.line_list[driver_file_index], check_msg)
            elif flag == "flash_driver":
                self.data_transfer(pcan, self.line_list[driver_file_index], self.max_block_size)
                # self.data_transfer(pcan, self.line_list[driver_file_index])
            elif flag == "exit_driver" or flag == "exit_app":
                check_msg = self.check_messages[key]  # 检查字符串
                self.transfer_exit(pcan, check_msg)
            elif flag == "check_crc_driver":
                check_msg = self.check_messages[key]  # 检查字符串
                self.check_crc(pcan, self.line_list[driver_file_index], check_msg)
            elif flag == "erase_memory":
                check_msg = self.check_messages[key]  # 检查字符串
                self.erase_memory(pcan, self.line_list[app_file_index], check_msg)
            elif flag == "request_app":
                check_msg = self.check_messages[key]  # 检查字符串
                self.max_block_size = self.request_download(pcan, self.line_list[app_file_index], check_msg)
            elif flag == "flash_app":
                self.data_transfer(pcan, self.line_list[app_file_index], self.max_block_size)
                # self.data_transfer(pcan, self.line_list[app_file_index])
            elif flag == "check_crc_app":
                check_msg = self.check_messages[key]  # 检查字符串
                self.check_crc(pcan, self.line_list[app_file_index], check_msg)
            elif flag == "check_dependence":
                check_msg = self.check_messages[key]  # 检查字符串
                self.check_program_dependence(pcan, check_msg)
            elif flag == "SF":
                check_msg = self.check_messages[key]  # 检查字符串
                self.send_check_single(pcan, send_msg, check_msg)
            elif flag == "thread":
                if val[1] == "start":
                    for each in val[2]:
                        json_msg = self.dataProcess.get_json_msg(self.thread_msg, each)
                        dict_thread[each] = CanThread(pcan, json_msg)
                    for each in dict_thread.keys():
                        dict_thread[each].start()

                elif val[1] == "stop":
                    for each in val[2]:
                        dict_thread[each].stop()

                elif val[1] == "restart":
                    for each in val[2]:
                        dict_thread[each].resume()

                elif val[1] == "pause":
                    for each in val[2]:
                        dict_thread[each].pause()

            time.sleep(delay_time)

    # 获取种子
    def security_seed(self, pcan, send_msg, check_msg):
        seed = []
        # can_message = ["7A1", "8", "02", "27", level, "00", "00", "00", "00", "00"]
        can_message = self.dataProcess.get_can_message(send_msg)
        pcan.write_request_messages(can_message)
        response_msg = pcan.check_response_msg(check_msg)
        if response_msg != None:
            for i in range(3, 7):
                seed.append(hex(response_msg.DATA[i])[2:].rjust(2, '0'))

        result = ""  # 将seed合成一个字符串返回
        for each in seed:
            result += each
        result = '0x' + result
        # print(result)
        return result

    # 进入安全访问
    def security_access(self, pcan, mask, seed, send_msg, check_msg, level):
        project = self.dataProcess.get_json_msg(self.json_data, "project")
        key_list = []
        if project == "NL-3B":
            key_list = security_geely(mask, seed, level)
        # 进入安全访问
        # can_message = ["7A1", "8", "06", "27", level, key_list[0], key_list[1], key_list[2], key_list[3], '00']
        can_message = self.dataProcess.get_can_message(send_msg)
        can_message[2] = "06"
        for i in range(4):
            can_message[i+5] = key_list[i]
        print(can_message)
        pcan.write_request_messages(can_message)
        response_msg = pcan.check_response_msg(check_msg)
        return response_msg

    # 发送单帧报文
    def send_check_single(self, pcan, send_msg, check_msg):
        can_message = self.dataProcess.get_can_message(send_msg)
        pcan.write_request_messages(can_message)
        rec_msg = pcan.check_response_msg(check_msg)
        # 获取单帧与多帧的标志位
        flag = hex(rec_msg.DATA[0])[2:].rjust(2, '0')
        if flag == '10':
            message_FC = self.dataProcess.get_json_msg(self.json_data, "message_FC")
            pcan.write_request_messages(message_FC)

    # 发送多帧报文
    def send_check_mult(self, pcan, send_msg, check_msg):
        can_message_list = self.dataProcess.get_can_message(send_msg)
        # for can_message in can_message_list:
        for index in range(len(can_message_list)):
            pcan.write_request_messages(can_message_list[index])
            if index == 0:
                pcan.check_response_msg(self.dataProcess.get_json_msg(self.json_data, "concat_msg,FC_check"))
        rec_msg = pcan.check_response_msg(check_msg)
        return rec_msg

    # 请求下载数据
    # send_msg 是一个二维 list, 第一个元素是list ,例如["7A1", "8"] , 第二个元素是一个字符串，例如"1001"
    def request_download(self, pcan, line_list, check_msg):
        send_msg = []
        send_msg.append(self.head_data)
        head = "340044"
        download_address = self.dataProcess.get_download_address(line_list).rjust(8, '0')
        data_size = self.dataProcess.get_data_size(line_list).rjust(8, '0')
        send_msg.append(head + download_address + data_size)
        response_msg = self.send_check_mult(pcan, send_msg, check_msg)
        max_block_size = hex(response_msg.DATA[3])[2:] + hex(response_msg.DATA[4])[2:]
        return int(max_block_size, 16)

    # 传输数据
    # dataLength:int
    # maxBlockSize:int
    def data_transfer(self, pcan, line_list, max_block_size=0x5B4):
        max_block_size = max_block_size - 2

        block_index = 0 # block 索引
        block_frame_index = 0  # 每一个block的帧数索引
        data_count = 0
        # subframe_count = 0
        frameCount_PerBlock = int((max_block_size - 4) / 7) + 1 # 每一个block 除去首帧，剩余的帧数
        data_size = int(self.dataProcess.get_data_size(line_list), 16)
        flash_data = self.dataProcess.get_flash_data(line_list)
        max_block_count = int(data_size/max_block_size) + 1
        send_msg = []

        for i in range(max_block_count):
            if block_index == 0xff:
                block_index = 0
            subframe_count = 0 # 最大值为15
            block_index += 1
            if block_frame_index == 0: # 第一个block的第一帧
                if data_size < max_block_size: # for flash driver
                    reqByte0 = hex(0x10 | ((data_size >> 8) & 0x0f))[2:]
                    reqByte1 = hex(data_size + 2)[3:]

                else:
                    if i == (max_block_count-1): # 最后一个block的第一帧
                        last_block_size = data_size - ((max_block_count-1) * max_block_size)  # 最后一个block的字节数
                        reqByte0 = hex(0x10 | ((last_block_size >> 8) & 0x0f))[2:]
                        reqByte1 = hex(last_block_size + 2)[3:]
                        # reqByte1 = hex(last_block_size)[3:]

                    else: # 其他block的第一帧
                        reqByte0 = hex(0x10 | ((max_block_size + 2 >> 8) & 0x0f))[2:]
                        reqByte1 = hex(max_block_size + 2)[3:]
                        # reqByte0 = hex(0x10 | ((max_block_size>> 8) & 0x0f))[2:]
                        # reqByte1 = hex(max_block_size)[3:]

                reqByte2 = '36'
                reqByte3 = hex(block_index)[2:].rjust(2, '0')
                reqByte4 = flash_data[data_count]
                reqByte5 = flash_data[data_count+1]
                reqByte6 = flash_data[data_count+2]
                reqByte7 = flash_data[data_count+3]
                data_count += 4
                send_msg.clear()
                send_msg.append(self.head_data)
                send_msg.append(reqByte0 + reqByte1 + reqByte2 + reqByte3 + reqByte4 + reqByte5 + reqByte6 + reqByte7)
                can_msg = self.dataProcess.get_can_message2(send_msg)
                # print("send_msg", send_msg)
                pcan.write_request_messages(can_msg)
                # 第一帧check是否收到流控帧
                pcan.check_response_msg("(.*)id=07A9 l=8(.*)30")
                block_frame_index = block_frame_index + 1

            if block_frame_index != 0:
                # 执行完这个循环就是一个完整的block
                for block_frame_index in range(block_frame_index, frameCount_PerBlock):
                    if block_frame_index == 1:
                        subframe_count = 1
                    reqByte0 = hex(0x20 | subframe_count)[2:]
                    reqByte1 = flash_data[data_count]
                    reqByte2 = flash_data[data_count+1]
                    reqByte3 = flash_data[data_count+2]
                    reqByte4 = flash_data[data_count+3]
                    reqByte5 = flash_data[data_count+4]
                    reqByte6 = flash_data[data_count+5]
                    reqByte7 = flash_data[data_count+6]
                    data_count += 7
                    send_msg.clear()
                    send_msg.append(self.head_data)
                    send_msg.append(reqByte0 + reqByte1 + reqByte2 + reqByte3 + reqByte4 + reqByte5 + reqByte6 + reqByte7)
                    can_msg = self.dataProcess.get_can_message2(send_msg)
                    pcan.write_request_messages(can_msg)
                    time.sleep(0.001)  # 必须稍微延时一小会

                    if subframe_count == 0x0F:
                        subframe_count = -1
                    subframe_count = subframe_count + 1

                    # 处理最后一个block的最后一行数据
                    if (block_index == max_block_count) and ((data_size - data_count) < 7):
                        if block_frame_index == 1:
                            subframe_count = 1
                        data_list = []
                        for n in range(data_count, data_size):
                            data_list.append(flash_data[n])
                        for n in range(7 - len(data_list)):
                            data_list.append('00')
                        reqByte0 = hex(0x20 | subframe_count)[2:]
                        reqByte1 = data_list[0]
                        reqByte2 = data_list[1]
                        reqByte3 = data_list[2]
                        reqByte4 = data_list[3]
                        reqByte5 = data_list[4]
                        reqByte6 = data_list[5]
                        reqByte7 = data_list[6]
                        data_count += (data_size - data_count)
                        send_msg.clear()
                        send_msg.append(self.head_data)
                        send_msg.append(reqByte0 + reqByte1 + reqByte2 + reqByte3 + reqByte4 + reqByte5 + reqByte6 + reqByte7)
                        can_msg = self.dataProcess.get_can_message2(send_msg)
                        pcan.write_request_messages(can_msg)
                        break

                # 处理block的最后一行数据
                if (block_index != max_block_count) and (max_block_size - 4 - 7*(frameCount_PerBlock-1) < 7):
                    if block_frame_index == 1:
                        subframe_count = 1
                    data_list = []
                    for n in range(data_count, max_block_size*block_index):
                        data_list.append(flash_data[n])
                    for n in range(7 - len(data_list)):
                        data_list.append('00')
                    reqByte0 = hex(0x20 | subframe_count)[2:]
                    reqByte1 = data_list[0]
                    reqByte2 = data_list[1]
                    reqByte3 = data_list[2]
                    reqByte4 = data_list[3]
                    reqByte5 = data_list[4]
                    reqByte6 = data_list[5]
                    reqByte7 = data_list[6]
                    data_count += (max_block_size*block_index - data_count)
                    send_msg.clear()
                    send_msg.append(self.head_data)
                    send_msg.append(reqByte0 + reqByte1 + reqByte2 + reqByte3 + reqByte4 + reqByte5 + reqByte6 + reqByte7)
                    can_msg = self.dataProcess.get_can_message2(send_msg)
                    pcan.write_request_messages(can_msg)
                    # print('send_msg', send_msg)

            # 每发送完一个block, 检查 response
            block_index_str = hex(block_index)[2:].rjust(2, '0')
            # (.*)为贪婪匹配
            check_msg = self.dataProcess.get_json_msg(self.json_data, "concat_msg,flash_data_check")
            pcan.check_response_msg(check_msg + block_index_str)
            # 一个block 完成，block_frame_index 置为0
            block_frame_index = 0


    # 退出传输
    def transfer_exit(self, pcan, check_msg):
        send_msg = []
        send_msg.append(self.head_data)
        send_msg.append('37')
        self.send_check_single(pcan, send_msg, check_msg)

    # 检查编程依赖性
    def check_program_dependence(self, pcan, check_msg):
        send_msg = []
        send_msg.append(self.head_data)
        send_msg.append("3101FF01")
        self.send_check_single(pcan, send_msg, check_msg)

    # 检查编程完整性(一致性)
    def check_crc(self, pcan, line_list, check_msg):
        send_msg = []
        send_msg.append(self.head_data)
        head = "31010202"
        crc_val = self.dataProcess.calc_crc32(line_list)
        send_msg.append(head + crc_val)
        self.send_check_mult(pcan, send_msg, check_msg)

    # 擦除内存
    def erase_memory(self, pcan, line_list, check_msg):
        send_msg = []
        send_msg.append(self.head_data)
        head = "3101FF0044"
        download_address = self.dataProcess.get_download_address(line_list).rjust(8, '0')
        data_size = self.dataProcess.get_data_size(line_list).rjust(8, '0')
        send_msg.append(head + download_address + data_size)
        # 发送多帧报文
        self.send_check_mult(pcan, send_msg, check_msg)


if __name__ == "__main__":
    pcan = Pcan(PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_MESSAGE_FILTER)
    data_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), '..')), "data")
    json_path = os.path.join(data_path, "message_03_3b.json")
    comm = ThreadMain(json_path, data_path)
    comm.send_check_messages(pcan)
