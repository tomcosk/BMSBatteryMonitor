import threading

class BaseThread (threading.Thread):
    def __init__(self, name = 'Basic Thread'):
        threading.Thread.__init__(self)
        self.name = name
        self.keepRunning = True
        self.isActive = False;

    def exit(self):
        self.keepRunning = False
