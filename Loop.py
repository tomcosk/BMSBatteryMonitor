import BaseThread
import time


class Loop (BaseThread.BaseThread):
    def __init__(self, name, websocketFactory, bms, display):
        BaseThread.BaseThread.__init__(self)
        self.factory = websocketFactory
        self.keepRunning = True
        self.name = name
        self.bms = bms
        self.oled = display

    def run(self):
        print('Loop started')
        self.isActive = True

        while self.keepRunning:
            connections = len(self.factory.clients)

            self.oled.draw.rectangle(
                (0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
            cells = self.bms.get_cells_info()
            basic_info = self.bms.get_basic_info()
            if cells is not None:
                self.oled.draw.text((0, self.oled.top+0), "1: " +
                                    str(cells['cell_0']/1000), font=self.oled.font, fill=255)
                self.oled.draw.text((64, self.oled.top+0), "2: " +
                                    str(cells['cell_1']/1000), font=self.oled.font, fill=255)
                self.oled.draw.text((0, self.oled.top+18), "3: " +
                                    str(cells['cell_2']/1000), font=self.oled.font, fill=255)
                self.oled.draw.text((64, self.oled.top+18), "4: " +
                                    str(cells['cell_3']/1000), font=self.oled.font, fill=255)
                self.oled.draw.text((0, self.oled.top+36), "5: " +
                                    str(cells['cell_4']/1000), font=self.oled.font, fill=255)
                self.oled.draw.text((64, self.oled.top+36), "6: " +
                                    str(cells['cell_5']/1000), font=self.oled.font, fill=255)
                self.oled.draw.text((0, self.oled.top+54), "7: " +
                                    str(cells['cell_6']/1000), font=self.oled.font, fill=255)

            if basic_info is not None:
                self.oled.draw.text((64, self.oled.top+54), "RSOC: " +
                                    str(basic_info['rsoc'])+"%", font=self.oled.font, fill=255)

            # Display image.
            self.oled.display.image(self.oled.img)
            try:
                self.oled.display.show()
            except:
                self.oled.__init__(128, 64, self.bms)
            # time.sleep(1)

            for client in self.factory.clients:
                if client.subscribed is True:
                    msgToSend = self.get_cells_info(7)
                    client.sendMessage(msgToSend.encode('utf-8'))

            time.sleep(.5)
        self.isActive = False
        print("Loop finished")
