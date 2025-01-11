import numpy as np
from pyflipdot.sign import HanoverSign
from pyflipdot.pyflipdot import HanoverController
from serial import Serial
from PIL import Image

#COM12 is my serial port, to be updated to your own
ser = Serial('COM12')
controller = HanoverController(ser)

#My Hanover is set to pin 1, address should always be increased by 1, width and height to be adjusted according to your display
sign = HanoverSign(address=2, width=144, height=19)
controller.add_sign('dev', sign)

# Load the image, my image is in the same directory as the python code
image = Image.open("skyline.jpg")

# Resize
image = image.resize((144, 19), Image.BILINEAR)

# Convert to grayscale
image = image.convert('L')

# Thresholding (convert to black and white)
threshold = 128  # Adjust this value (0-255) to fine-tune the result
image = image.point(lambda p: 255 if p > threshold else 0)

# Convert to a NumPy array (important: convert to boolean array)
image_array = np.array(image, dtype=bool)

# Write the image to the sign
controller.draw_image(image_array)