#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Author : yangwei.li
@Create date : 2019-10-30
@FileName : security_algorithm.py
"""

from mode_process.data_process import DataProcess

# 安全访问算法

def security_geely(mask, seed, level):
    retKey = []
    calData = []
    if type(seed) == str:
        seed = eval(seed)
    if type(seed) == str:
        mask = eval(mask)

    seed = hex(seed)[2:].rjust(8, '0')
    mask = hex(mask)[2:].rjust(8, '0')
    seed_list = DataProcess().cut_text(seed, 2)
    mask_list = DataProcess().cut_text(mask, 2)
    for i in range(4):
        calData.append(int(seed_list[i], 16) ^ int(mask_list[i], 16))
    if level == "app_access":
        retKey.clear()
        retKey.append(hex(((calData[3] & 0x0F) << 4) | (calData[3] & 0xF0)))
        retKey.append(hex(((calData[1] & 0x0F) << 4) | ((calData[0] & 0xF0) >> 4)))
        retKey.append(hex((calData[1] & 0xF0) | ((calData[2] & 0xF0) >> 4)))
        retKey.append(hex(((calData[0] & 0x0F) << 4) | (calData[2] & 0x0F)))

    if level == "boot_access":
        retKey.clear()
        retKey.append(hex(((calData[2] & 0x03) << 6) | ((calData[3] & 0xFC) >> 2)))
        retKey.append(hex(((calData[3] & 0x03) << 6) | (calData[0] & 0x3F)))
        retKey.append(hex((calData[0] & 0xFC) | ((calData[1] & 0xC0) >> 6)))
        retKey.append(hex((calData[1] & 0xFC) | (calData[2] & 0x03)))

    # result_str = "" # 将key合成一个字符串返回
    # for each in retKey:
    #     result_str += each[2:].rjust(2, '0')
    # result_str = '0x' + result_str

    result_list = []
    for each in retKey:
        result_list.append(each[2:].rjust(2, '0'))
    return result_list


def geely_algorithm(mask, seed):
    cal = []
    key = [0x00, 0x00, 0x00, 0x00]

    if type(seed) == str:
         seed = eval(seed)
    if type(mask) == str:
         mask = eval(mask)
    seed = hex(seed)[2:].rjust(8, '0')
    mask = hex(mask)[2:].rjust(8, '0')
    seed_list = DataProcess().cut_text(seed, 2)
    mask_list = DataProcess().cut_text(mask, 2)

    for i in range(4):
        cal.append(int(seed_list[i], 16) ^ int(mask_list[i], 16))

    key[0] = hex(((cal[3] & 0x0F) << 4) | (cal[3] & 0xF0))
    key[1] = hex(((cal[1] & 0x0F) << 4) | ((cal[0] & 0xF0) >> 4))
    key[2] = hex((cal[1] & 0xF0) | ((cal[2] & 0xF0) >> 4))
    key[3] = hex(((cal[0] & 0x0F) << 4) | (cal[2] & 0x0F))
    print(key)

    # result_key = ""
    # for key_i in key:
    #     result_key += key_i[2:].rjust(2, '0')

    result_list = []
    for each in key:
        result_list.append(each[2:].rjust(2, '0'))

    return result_list



if __name__ == "__main__":
    key1_list = security_geely(0x1DD47818, 0x004EF52F, 'app')
    print('key1_list', key1_list)
    # seed = 0x004ef52f
    # seed = hex(seed)[2:].rjust(8, '0')
    # seed_list = DataProcess().cut_text(seed, 2)
    # result = []
    # for i in range(4):
    #     result.append(hex(int(seed_list[i], 16)))
    # print(result)
    #
    # key2 = geely_algorithm(result)
    # print('key2',key2)

    # key2_list = geely_algorithm(0x1DD47818, 0x004EF52F)
    # print('key_list', key2_list)

