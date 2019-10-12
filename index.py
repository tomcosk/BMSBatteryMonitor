# many inspiration got from here https://endless-sphere.com/forums/viewtopic.php?t=91672
# and basic communication is based on this https://github.com/simat/BatteryMonitor/wiki

import bmscore
import binascii
import sys
import json

ser = bmscore.openbms()


def rdjson(file):
    with open(file, "r") as read_file:
        data = json.load(read_file)
    return data


protocol_config = rdjson("protocolConfig.json")


def get_vendor():
    data = bmscore.getbmsdat(ser, bytes.fromhex(protocol_config['vendor']['command']))
    text = str(binascii.unhexlify(binascii.hexlify(data)))
    return text


def get_basic_info():
    data = bmscore.getbmsdat(ser, bytes.fromhex(
        protocol_config['basicInfo']['command']))
    reply = {}
    for key in protocol_config['basicInfo']['replyDataStringBytes']:
        byte_from = protocol_config['basicInfo']['replyDataStringBytes'][key]['from']
        byte_to = protocol_config['basicInfo']['replyDataStringBytes'][key]['to']
        reply[key] = int(binascii.hexlify(data[byte_from:byte_to]), 16)
    # reply['overall_current'] = int(binascii.hexlify(data[2:4]), 16)
    # reply['residual_capacity'] = int(binascii.hexlify(data[4:6]), 16)
    # reply['nominal_capacity'] = int(binascii.hexlify(data[6:8]), 16)
    # reply['cycle_times'] = int(binascii.hexlify(data[8:10]), 16)
    # reply['rsoc'] = int(binascii.hexlify(data[19:20]), 16)
    # reply['battery_serial_number'] = int(binascii.hexlify(data[21:22]), 16)
    # reply['ntc_quantity'] = int(binascii.hexlify(data[22:23]), 16)

    start_byte = 23
    for i in range(0, reply['ntc_quantity']):
        reply['ntc_'+str(i)+'_kelvin'] = int(
            binascii.hexlify(data[start_byte:start_byte+2]), 16)
        reply['ntc_'+str(i)+'_celsius'] = round(kelvin2celsius(
            int(binascii.hexlify(data[start_byte:start_byte+2]), 16)/10)*100)/100
        start_byte = start_byte + 2

    return reply


def get_cells_info(num_series):
    data = bmscore.getbmsdat(ser, bytes.fromhex(
        protocol_config['cellsInfo']['command']))
    start_byte = 0
    reply = {}
    for i in range(0, num_series):
        # print("reading cell: "+str(start_byte)+":"+str(start_byte+2))
        reply['cell_' +
              str(i)] = int(binascii.hexlify(data[start_byte:start_byte+2]), 16)
        start_byte = start_byte + 2
    return reply


def read_settings():
    for command in protocol_config['settings']['commandSequence']:
        data = bmscore.getbmsdat(ser, bytes.fromhex(command))

    reply = {}
    for key in protocol_config['settings']['registers']:
        data = bmscore.getbmsdat(ser, bytes.fromhex(
            protocol_config['settings']['registers'][key]['command']))
        reply[key] = int(binascii.hexlify(data), 16)

    return reply


def kelvin2celsius(temp):
    return temp-273.15


print(get_vendor())
print(get_basic_info())
print(get_cells_info(7))
print(read_settings())

# command = bytes.fromhex('DD 5A 00 02 56 78 FF 30 77')
# data = bmscore.getbmsdat(ser, command)

# command = bytes.fromhex('dd a5 25 00 ff db 77')
# data = bmscore.getbmsdat(ser, command)
# command = bytes.fromhex('dd 24 00 02 10 9a ff 54 77')
# data = bmscore.getbmsdat(ser, command)
# text = binascii.b2a_hex(binascii.hexlify(data))
# print(text)


# print(get_vendor())

# command = bytes.fromhex('dd 5a 00 02 56 78 ff 30 77')
# data = bmscore.getbmsdat(ser, command)
# 0f1a0eac0eaf0eb70eec0f230eb9
# print(data)
# 0a610000
# 071907d000002687000000000000205b0307020b7c0b71
