# many inspiration got from here https://endless-sphere.com/forums/viewtopic.php?t=91672
# and basic communication is based on this https://github.com/simat/BatteryMonitor/wiki

import bmscore
from bms import Bms
from Oled import Oled
from Loop import Loop
import sys
import json
import signal
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

protocol_config = bmscore.rdjson("protocolConfig.json")
ser = bmscore.openbms()
bms = Bms(ser, protocol_config)


display = Oled(128, 64, bms)
display.splash("BMS", bms.vendor)


def signal_handler(signal, frame):
    global keep_running
    keep_running = False
    loop.exit()

    print("Received SIGINT - Shutting down")
    reactor.stop()


print(bms.get_vendor())
print(bms.get_basic_info())
print(bms.get_cells_info())
print(bms.read_settings())


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


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    factory.clients = []

    # note to self: if using putChild, the child must be bytes...

    loop = Loop('Periodic Loop', factory, bms, display)

    loop.start()

    signal.signal(signal.SIGINT, signal_handler)

    reactor.listenTCP(9000, factory)
    reactor.run()
