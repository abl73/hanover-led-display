from pyflipdot.pyflipdot import HanoverController
from pyflipdot.sign import HanoverSign
from serial import Serial
from PIL import Image, ImageDraw, ImageFont
import time
import numpy as np

# Hanover Display Configuration
ser = Serial('/dev/ttyUSB0')  # Adjust serial port if needed
controller = HanoverController(ser)
sign = HanoverSign(address=2, width=144, height=19) # Adjust serial port if needed, mine at dial 1 and 144x19 pixels
controller.add_sign('office', sign)

def display_image(image_path):
    """Displays an image from a file on the Hanover display."""
    try:
        image = Image.open(image_path).convert("L")  # Open and convert to grayscale
        image = image.resize((sign.width, sign.height), Image.Resampling.LANCZOS) #resize image

        # Threshold to create a pure black and white image
        threshold = 128  # Adjust this value if needed
        image = image.point(lambda p: p > threshold and 255)

        sign_image = np.array(image)
        sign_image = np.where(sign_image, True, False)

        controller.draw_image(sign_image)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
    except Exception as e:
        print(f"Error displaying image: {e}")

try:
    display_image("skyline.jpg")  # Display the image, saved in same directory as script

    while True: # Keep the script running
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    empty_image = sign.create_image()
    controller.draw_image(empty_image)
    ser.close()