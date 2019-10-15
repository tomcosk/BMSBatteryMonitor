import time
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


class Oled():
    def __init__(self, width, height, bms):
        self.bms = bms
        self.i2c = busio.I2C(SCL, SDA)
        self.width = width
        self.height = height
        self.display = adafruit_ssd1306.SSD1306_I2C(
            self.width, self.height, self.i2c)
        # Clear display.
        self.display.fill(0)
        self.display.show()
        self.img = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = draw = ImageDraw.Draw(self.img)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        self.top = padding
        self.bottom = height-padding
        # Move left to right keeping track of the current x position for drawing shapes.

    def splash(self, title, vendor):
        self.font = ImageFont.truetype('./Arial-Black.ttf', 19)
        self.draw.text((40, self.top+10), title, font=self.font, fill=255)

        self.font = ImageFont.truetype('./Arial-Black.ttf', 11)
        if vendor is not None:
            self.draw.text((10, self.top+50), str(vendor),
                           font=self.font, fill=255)
        # Display image.
        self.display.image(self.img)
        self.display.show()

        # Load default font.
        self.font = ImageFont.load_default()
        time.sleep(5)
