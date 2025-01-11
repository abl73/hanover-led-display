import numpy as np
from pyflipdot.sign import HanoverSign
from pyflipdot.pyflipdot import HanoverController
from serial import Serial
from PIL import Image, ImageDraw, ImageFont

ser = Serial('COM12')
controller = HanoverController(ser)
sign = HanoverSign(address=2, width=144, height=19)
controller.add_sign('dev', sign)

# Create an empty image with Pillow
width, height = 144, 19
image = Image.new("1", (144, 19), color=0)  # Create a monochrome image
draw = ImageDraw.Draw(image)

# Optional: Load a font (adjust size as needed)
# Replace with a path to a .ttf font file if you have one, or use the default
font = ImageFont.truetype("hanover-11x19.ttf", 19)  # Adjust font size to fit the sign
#font = ImageFont.load_default()

# Measure the text size using getbbox
text = "Hello World!"
bbox = font.getbbox(text)  # Returns (x_min, y_min, x_max, y_max)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Calculate position to center the text
x = (width - text_width) // 2  # Center horizontally
y = (height - text_height) // 2  # Center vertically

# Draw the text on the image
draw.text((x, y), text, fill=1, font=font)

# Convert the Pillow image to a NumPy array compatible with pyflipdot
image_array = np.array(image)

# Write the image to the sign
controller.draw_image(image_array)
