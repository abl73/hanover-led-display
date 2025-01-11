import numpy as np
import paho.mqtt.client as mqtt
from pyflipdot.sign import HanoverSign
from pyflipdot.pyflipdot import HanoverController
from serial import Serial
from PIL import Image, ImageDraw, ImageFont
import time

# MQTT broker details
#if broker is for instance 192.168.178.50 -> broker = "192.168.178.50"
broker = "<ip address of the MQTT broker>"
port = 1883 #typical port number for MQTT
#username and password to be adjusted so that mqtt broker can be used
username = "<username>"
password = "<password>"
# Topic to subscribe to
topic = "hanover/display"  

# Create serial connection
ser = Serial('COM12')  # Update with your serial port

# Create a controller
controller = HanoverController(ser)

# Define the sign dimensions and address
#My Hanover display was set to dial/dipswitch 1, so +1 = 2)
sign = HanoverSign(address=2, width=144, height=19)
controller.add_sign('dev', sign)

# Create an empty image with Pillow
width, height = 144, 19
image = Image.new("1", (144, 19), color=0)  # Create a monochrome image
draw = ImageDraw.Draw(image)

# Optional: Load a font (adjust size as needed)
font = ImageFont.truetype("hanover-11x19.ttf", 19)  # Adjust font size to fit the sign

# This function will be called when a message is received from the MQTT broker
def on_message(client, userdata, msg):
    text = msg.payload.decode("utf-8")  # Decode the message payload to a string
    print(f"Received message: {text}")

    # Measure the text size using getbbox
    bbox = font.getbbox(text)  # Returns (x_min, y_min, x_max, y_max)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position to center the text
    x = (width - text_width) // 2  # Center horizontally
    y = (height - text_height) // 2  # Center vertically

    # Clear the image before drawing new text
    image = Image.new("1", (144, 19), color=0)
    draw = ImageDraw.Draw(image)

    # Draw the new text on the image
    draw.text((x, y), text, fill=1, font=font)

    # Convert the Pillow image to a NumPy array compatible with pyflipdot
    image_array = np.array(image)

    # Write the image to the sign
    controller.draw_image(image_array)

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set(username, password)  # Set username and password
client.on_message = on_message  # Set the message handler

# Connect to the broker
client.connect(broker, port)

# Subscribe to the topic
client.subscribe(topic)

# Start the MQTT loop to listen for messages
client.loop_start()

# Keep the program running
try:
    while True:
        time.sleep(1)  # Sleep to allow MQTT messages to be processed
except KeyboardInterrupt:
    print("Exiting...")

# Stop the MQTT loop when exiting
client.loop_stop()
