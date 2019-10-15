import bmscore
import binascii
import time


class Bms():
    def __init__(self, serial, config):
        self.serial = serial
        self.protocol_config = config
        self.num_cells = None
        self.set_num_cells()
        self.vendor = None
        while self.vendor is None:
            self.vendor = self.get_vendor()
            time.sleep(1)

    def set_num_cells(self):
        self.num_cells = self.get_basic_info()["battery_serial_number"]

    def get_vendor(self):
        data = bmscore.getbmsdat(self.serial, bytes.fromhex(
            self.protocol_config['vendor']['command']))
        if data is not None:
            text = str(binascii.unhexlify(binascii.hexlify(data)))
        else:
            text = 'Unknown'
        return text

    def get_basic_info(self):
        data = bmscore.getbmsdat(self.serial, bytes.fromhex(
            self.protocol_config['basicInfo']['command']))
        reply = {}
        if data is not None:
            for key in self.protocol_config['basicInfo']['replyDataStringBytes']:
                byte_from = self.protocol_config['basicInfo']['replyDataStringBytes'][key]['from']
                byte_to = self.protocol_config['basicInfo']['replyDataStringBytes'][key]['to']
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
                reply['ntc_'+str(i)+'_celsius'] = round(self.kelvin2celsius(
                    int(binascii.hexlify(data[start_byte:start_byte+2]), 16)/10)*100)/100
                start_byte = start_byte + 2
        else:
            return None

        return reply

    def get_cells_info(self):
        while self.num_cells is None:
            self.set_num_cells
            time.sleep(1)

        data = bmscore.getbmsdat(self.serial, bytes.fromhex(
            self.protocol_config['cellsInfo']['command']))
        reply = {}
        if data is not None:
            start_byte = 0
            for i in range(0, self.num_cells):
                # print("reading cell: "+str(start_byte)+":"+str(start_byte+2))
                reply['cell_' +
                      str(i)] = int(binascii.hexlify(data[start_byte:start_byte+2]), 16)
                start_byte = start_byte + 2
        else:
            return None
        return reply

    def read_settings(self):
        for command in self.protocol_config['settings']['commandSequence']:
            data = bmscore.getbmsdat(self.serial, bytes.fromhex(command))

        reply = {}
        for key in self.protocol_config['settings']['registers']:
            data = bmscore.getbmsdat(self.serial, bytes.fromhex(
                self.protocol_config['settings']['registers'][key]['command']))
            reply[key] = int(binascii.hexlify(data), 16)

        return reply

    def kelvin2celsius(self, temp):
        return temp-273.15
