from pyflipdot.pyflipdot import HanoverController
from pyflipdot.sign import HanoverSign
from serial import Serial
from PIL import Image, ImageDraw, ImageFont
import time
import numpy as np  # Import numpy explicitly

#To be changed to serial port used on your RPI
ser = Serial('/dev/ttyUSB0')
controller = HanoverController(ser)

#To be changed to specifics of your hanover display (mine: dial at 1, 144x19 pixels)
sign = HanoverSign(address=2, width=144, height=19)
controller.add_sign('office', sign)

def text_to_image(text, width, height, font_path=None):
    """Converts text to a black and white PIL Image."""
    image = Image.new('1', (width, height), 0)
    draw = ImageDraw.Draw(image)

    try:
        if font_path:
            font = ImageFont.truetype(font_path, 19)
        else:
            font = ImageFont.load_default()
    except OSError:
        print(f"Font not found: {font_path}. Using default font.")
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, font=font, fill=1)
    return image

def display_text(text):
    """Displays text on the Hanover display (Corrected Pixel Transfer)."""
    image = text_to_image(text, sign.width, sign.height, "hanover-11x19.ttf")

    # Corrected pixel transfer using numpy
    sign_image = np.array(image)
    sign_image = np.where(sign_image, True, False) #convert 255 to True, 0 to False

    controller.draw_image(sign_image)

try:
    while True:
        display_text("Hello")
        time.sleep(2)
        display_text("World")
        time.sleep(2)
        display_text("012345678901234")
        time.sleep(2)
        display_text("abcdefghijklmno")
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    empty_image = sign.create_image()
    controller.draw_image(empty_image)
    ser.close()