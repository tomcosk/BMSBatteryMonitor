# many inspiration got from here https://endless-sphere.com/forums/viewtopic.php?t=91672
# and basic communication is based on this https://github.com/simat/BatteryMonitor/wiki

import bmscore
import binascii
import sys
import json
import string
import BaseThread
import signal
import time
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

APP_DIR = "/home/pi/BMSBatteryMonitor/"

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
font = ImageFont.truetype(APP_DIR+'Arial-Black.ttf', 19)
draw.text((40, top+20), "BMS", font=font, fill=255)

# Display image.
disp.image(image)
disp.show()


# Load default font.
font = ImageFont.load_default()

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

ser = bmscore.openbms()


def signal_handler(signal, frame):
    global keep_running
    keep_running = False
    loop.exit()

    print("Received SIGINT - Shutting down")
    reactor.stop()

def rdjson(file):
    with open(file, "r") as read_file:
        data = json.load(read_file)
    return data


protocol_config = rdjson(APP_DIR+"protocolConfig.json")


def get_vendor():
    data = bmscore.getbmsdat(ser, bytes.fromhex(
        protocol_config['vendor']['command']))
    text = str(binascii.unhexlify(binascii.hexlify(data)))
    return text


def get_basic_info():
    data = bmscore.getbmsdat(ser, bytes.fromhex(
        protocol_config['basicInfo']['command']))
    reply = {}
    if data is not None:
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
    else:
        return None

    return reply


def get_cells_info(num_series):
    data = bmscore.getbmsdat(ser, bytes.fromhex(
        protocol_config['cellsInfo']['command']))
    reply = {}
    if data is not None:
        start_byte = 0
        for i in range(0, num_series):
            # print("reading cell: "+str(start_byte)+":"+str(start_byte+2))
            reply['cell_' +
                  str(i)] = int(binascii.hexlify(data[start_byte:start_byte+2]), 16)
            start_byte = start_byte + 2
    else:
        return None
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


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.factory.clients.append(self)
        self.authenticated = False
        self.subscribed = False
        self.factory.numClients = self.factory.numClients + 1
        self.userId = self.id_generator(size=10)
        self.name = None

    def onOpen(self):
        pass
#        print("WebSocket connection open.")

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def onMessage(self, payload, isBinary):
        global cached_img
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

            obj = json.loads(payload.decode('utf8'))
            print(obj['command'])
            msgToSend = ''

            if obj['command'] == 'SUBSCRIBE':
                self.subscribed = True

            elif obj['command'] == 'INIT':
                pass
                # func = getattr(self.factory.executer, 'init')
                # msgToSend = func()
                # print(msgToSend)
                # self.sendMessage(msgToSend.encode('utf-8'))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def connectionLost(self, reason):
        print('connection lost: '+reason.getErrorMessage())
        self.factory.numClients = self.factory.numClients - 1
        self.factory.clients.remove(self)
        msg = {
            'type': 'USER_LEFT',
            'value': self.userId
        }
        msgToSend = json.dumps(msg)
        for client in self.factory.clients:
            if self.name is not None:
                client.sendMessage(msgToSend.encode('utf-8'))


class Loop (BaseThread.BaseThread):
    def __init__(self, name, websocketFactory):
        BaseThread.BaseThread.__init__(self)
        self.factory = websocketFactory
        self.keepRunning = True
        self.name = name

    def run(self):
        print('Loop started')
        self.isActive = True

        while self.keepRunning:
            connections = len(self.factory.clients)

            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            cells = get_cells_info(7)
            basic_info = get_basic_info()
            if cells is not None:
                draw.text((x, top+0), "1: "+str(cells['cell_0']/1000), font=font, fill=255)
                draw.text((64, top+0), "2: "+str(cells['cell_1']/1000), font=font, fill=255)
                draw.text((x, top+18), "3: "+str(cells['cell_2']/1000), font=font, fill=255)
                draw.text((64, top+18), "4: "+str(cells['cell_3']/1000), font=font, fill=255)
                draw.text((x, top+36), "5: "+str(cells['cell_4']/1000), font=font, fill=255)
                draw.text((64, top+36), "6: "+str(cells['cell_5']/1000), font=font, fill=255)
                draw.text((x, top+54), "7: "+str(cells['cell_6']/1000), font=font, fill=255)

            if basic_info is not None:
                draw.text((64, top+54), "RSOC: "+str(basic_info['rsoc'])+"%", font=font, fill=255)

            # Display image.
            disp.image(image)
            disp.show()
            # time.sleep(1)

            for client in self.factory.clients:
                if client.subscribed is True:
                    msgToSend = get_cells_info(7)
                    client.sendMessage(msgToSend.encode('utf-8'))




            time.sleep(.5)
        self.isActive = False
        print("Loop finished")


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    factory.clients = []

    # note to self: if using putChild, the child must be bytes...

    loop = Loop('Periodic Loop', factory)

    loop.start()

    signal.signal(signal.SIGINT, signal_handler)

    reactor.listenTCP(9000, factory)
    reactor.run()
