#!/usr/bin/python
# *****Core routines to retrieve and store data to BMS PCBs*****
# Copyright (C) 2017 Simon Richard Matthews
# Project loaction https://github.com/simat/BatteryMonitor
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import time
import serial
import binascii
import json


def crccalc(data):
    """returns crc as integer from byte stream"""
    crc = 0x10000
    for i in data:
        crc = crc-int(i)
    return crc


def openbms(port='/dev/ttyUSB0'):
    ser = serial.Serial(port)  # open serial port
    ser.timeout = 3
    return ser


def getbmsdat(port, command):
    """ Issue BMS command and return data as byte data """
    """ assumes data port is open and configured """
    # print('command=', binascii.hexlify(command))
    port.write(command)
    reply = port.read(4)    # read 4 bytes. Headers commands etc.
    # read bytes 3 and 4. length of data
    length = int.from_bytes(reply[3:5], byteorder='big')
    data = port.read(length)  # read data bytes
    end = port.read(3)
    if len(data) < length:
        print('Serial Timeout')
    # if crccalc(reply[2:4]+data) != int.from_bytes(end[0:2], byteorder='big'):
    #     print('CRC Error')
    # print('reply=', binascii.hexlify(data))
    return data
