#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Author : yangwei.li
@Create date : 2019-10-23
@FileName : mode_process.py
"""

import re
import json
from device.pcan.PCANBase import Pcan
from device.pcan.PCANBasic import *
from util.invalid_exception import InvalidException
import os

crc32tab = [
    0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
    0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988, 0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91,
    0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE, 0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7,
    0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC, 0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5,
    0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172, 0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B,
    0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940, 0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59,
    0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116, 0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F,
    0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924, 0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D,
    0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A, 0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433,
    0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818, 0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01,
    0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E, 0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457,
    0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C, 0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65,
    0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2, 0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB,
    0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0, 0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9,
    0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086, 0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F,
    0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4, 0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD,
    0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A, 0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683,
    0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8, 0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1,
    0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE, 0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7,
    0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC, 0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5,
    0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252, 0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,
    0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60, 0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79,
    0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236, 0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F,
    0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04, 0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D,
    0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A, 0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713,
    0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38, 0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21,
    0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E, 0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777,
    0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C, 0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45,
    0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2, 0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB,
    0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0, 0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9,
    0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6, 0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF,
    0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94, 0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D]

class DataProcess():

    def __init__(self):
        pass

    # 获取路径下的所有特定后缀名的文件；考虑路径为具体某文件; sort_flag 默认不需要对文件按创建时间排序
    def get_file_list(self, file_path, file_suffix, sort_flag=False):
        file_list = []
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path) \
                    and os.path.splitext(file_path)[1].lower() in file_suffix:
                file_list.append(file_path)
            elif os.path.exists(file_path) and os.path.isdir(file_path):
                file_all = os.listdir(file_path)
                for each in file_all:
                    cur_file = os.path.join(file_path, each)
                    if os.path.exists(cur_file) and os.path.splitext(cur_file)[1].lower() in file_suffix:
                        file_list.append(os.path.join(file_path, each))
            else:
                print("the input path is wrong")
            if len(file_list) > 0:
                if sort_flag:
                    file_list = sorted(file_list, key=lambda x: os.path.getctime(x), reverse=False)
                return file_list
            else:
                print('no file !!!')
        except Exception as e:
            print(e)

    # 读取文件内容
    def open_file(self, file_path):
        with open(file_path, 'r') as f:
            line_list = f.readlines()
        return line_list

    # 读取文件夹下特定后缀名的文件
    def open_files(self, file_path):
        file_line_list = []
        file_list = self.get_file_list(file_path, ['.srec'])
        for file in file_list:
            with open(file, 'r') as f:
                line_list = f.readlines()
            file_line_list.append(line_list)
        return file_line_list

    # 读取json文件
    # return : dict
    def read_json_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data is not None:
                return data
        except Exception as e:
            print(e)

    # 根据关键字从json中获取data
    # return：dict or list or str
    def get_json_msg(self, data, keys):
        key_list = keys.split(',')
        try:
            for each in key_list:
                data = data[each]
        except KeyError:
            data = None
        return data

    # 按照固定长度分割字符串
    # 返回一个list
    def cut_text(self, text, length):
        textArr = re.findall('.{' + str(length) + '}', text)
        # print(len(textArr))
        if len(textArr) * length != len(text):
            textArr.append(text[(len(textArr) * length):])

        if len(textArr[-1]) < length:
            textArr[-1] = textArr[-1].ljust(length, '0')
        return textArr

    # 获取一条完整的can报文
    # ['7A1', '8', '02', '10', '02', '00', '00', '00', '00', '00'] 包含ID,length,message
    # msg_str_list 是一个list
    def get_can_message(self, msg_str_list):
        head_data = msg_str_list[0]
        msg_str = msg_str_list[-1]
        can_out = []
        len_msg = len(msg_str)
        hex_len = hex(len_msg//2)[2:].rjust(2, '0')
        # head_data = ["7A1", "8"]

        count = 0
        if len_msg > 7*2:
            # first frame
            FF_msg = head_data + self.cut_text('10' + hex_len + msg_str[0:12], 2)
            can_out.append(FF_msg)
            can_list = self.cut_text(msg_str[12:], 7 * 2)
            for each in can_list:
                count += 1
                can_msg = head_data + self.cut_text('2' + hex(count)[2:] + each, 2)
                can_out.append(can_msg)
        else:
            can_list = self.cut_text(msg_str, 7*2)
            can_out = head_data + self.cut_text(hex_len + can_list[0], 2)
        return can_out

    # 拆分拼接报文
    # 如['2c40000000000000'] --> ['7A1', '8', '2c', '40', '00', '00', '00', '00', '00', '00']
    def get_can_message2(self, msg_str):
        head_data = msg_str[0]
        msg_str = msg_str[-1]
        # head_data = ["7A1", "8"]
        can_out = head_data + self.cut_text(msg_str, 2)
        return can_out

    # 获取S3开始的行数
    def find_s3_start(self, lineList):
        # 获取file行数
        lineSize = len(lineList)
        for i in range(lineSize):
            if str(lineList[i]).startswith("S3"):
                s3StartIndex = i  # S3 开始的行数
                # print("find S3 start index: ", s3StartIndex)
                # print(line_list[s3StartIndex])
                # print(len(line_list[s3StartIndex].strip('\n')))
                return s3StartIndex

        print("can not find S3 start")
        return -1

    # 获取下载地址
    def get_download_address(self, line_list):
        s3StartIndex = self.find_s3_start(line_list)
        address = line_list[s3StartIndex][4:12]
        # print(address)
        return address

    # 获取刷写数据长度
    def get_data_size(self, line_list):
        data_size = 0
        for line in line_list:
            if str(line).startswith('S3'):
                data_size += len(line.strip("\n")[12:-2])
        data_size = hex(data_size // 2)[2:]
        return data_size

    # 获取flash data
    def get_flash_data(self, line_list):
        data_str = ""
        for line in line_list:
            if str(line).startswith('S3'):
                data_str += line.strip("\n")[12:-2]
        data_list = self.cut_text(data_str, 2)
        return data_list

    # 计算CRC32校验值
    def calc_crc32(self, line_list):
        crcval = 0xFFFFFFFF
        data_str = ""
        for line in line_list:
            data_str += line.strip("\n")[12:-2]
        data_list = self.cut_text(data_str, 2)
        data_length = len(data_list)
        for i in range(0, data_length):
            tabIndex = ((crcval ^ int(data_list[i], 16)) & 0xFF) & 0xFFFFFFFF
            crcval = ((crcval >> 8) & 0xFFFFFFFF) ^ crc32tab[tabIndex]
        crcval = hex(crcval ^ 0xFFFFFFFF)[2:]
        # print(crcval)
        return crcval


if __name__ == "__main__":
    pcan = Pcan(PCAN_USBBUS1, PCAN_BAUD_500K, PCAN_MESSAGE_FILTER)
    fp = DataProcess()
    json_data = fp.read_json_file("../date/message_03_3b.json")
    print(json_data)
    # json_msg = fp.get_json_msg(json_data, "concat_msg,head_data")
    # print(json_msg)
    # print(type(json_msg))
    # print(fp.get_can_message(['2c', '40', '00', '00', '00', '00', '00', '00']))
    # print(fp.cut_text('123', 7*2))
    # print(json_msg)
    # data = fp.get_json_can(json_msg)
    # print("data:", data)
    # can_msg = fp.get_can_message(json_msg[1])
    # print(can_msg)
    # pcan.write_request_messages(can_msg)

    # can_msg = fp.get_can_message("2EF186123456789abcdef")
    # print(can_msg)
    # data_list = fp.cut_text('2EF1120101010202020303', 2)
    # print(data_list)
    # can = fp.get_can_message(['2EF1120101010202020303'])
    # print(can)
    # path = os.path.join(os.path.abspath(os.path.join(os.getcwd(),'..')), "data")
    # print(path)
    # print(fp.get_file_list(path,['.srec']))
    # path = "../data/flash_driver.srec"
    # path = "../data"
    # line_list = fp.open_files(path)
    # print(line_list)

    # fp.find_s3_start(line_list)
    # address = fp.get_download_address(line_list)
    # print(address)
    # data_size = fp.get_data_size(line_list)
    # print(data_size)
    # data = "1520006D2080B586B000AFF8600B467A607B81012380"
    # data = fp.cut_text(data, 2)
    # print(data)
    # data_list = fp.get_flash_data(line_list)
    # print(data_list)

    # crc = fp.calc_crc32(line_list)
    # print(crc)
    # print(int(264))
    # file_list = fp.get_file_list(path,['.srec'])
    # print(file_list)
    # 回退到上一级路径
    # print(os.path.abspath(os.path.join(os.getcwd(),'..')))

    # path = "../data/flash_driver.srec"
    # line_list = fp.open_file(path)
    # send_msg = []
    # head = "3101FF0044"
    # download_address = fp.get_download_address(line_list).rjust(8, '0')
    # print('address ', download_address)
    # data_size = fp.get_data_size(line_list).rjust(8, '0')
    # print('size ', data_size)
    # send_msg.append(head + download_address + data_size)
    # can_msg = fp.get_can_message(send_msg)
    # print(can_msg)
