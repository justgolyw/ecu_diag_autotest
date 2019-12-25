#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 注意：python3 中需要pip install pyserial
import serial
import time

class PowerControl:

    # 获取串口状态
    def getStatus(self, ser):
        return ser.portstr

    # 设置电压值
    def setVol(self, value, ser):
        value_str = "Volt " + str(value) + "\n"
        ser.write(bytes(value_str, encoding='utf-8'))
        print("set voltage to %dV " % value)

    def powerOn(self, ser):
        ser.write(b"SYSTem:REMote\n")  # Set remote control
        ser.write(b"OUTPUT 1\n")
        print("power on...")

    def powerOff(self, ser):
        ser.write(b"SYSTem:REMote\n")  # Set remote control
        ser.write(b"OUTPUT 0\n")
        print("power off...")

    # 电压控制
    def voltageControl(self, value, ser):
        # ser.write(b"SYSTem:REMote\n") # Set remote control
        # ser.write(b"OUTPUT 1\n")
        # print("power on...")
        # time.sleep(1)
        ser.write(b"Appl ch1\n")  # Set ch1
        self.setVol(value, ser)
        # time.sleep(1)


