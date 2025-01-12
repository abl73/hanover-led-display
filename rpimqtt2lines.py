from pyflipdot.pyflipdot import HanoverController
from pyflipdot.sign import HanoverSign
from serial import Serial
from PIL import Image, ImageDraw, ImageFont
import time
import numpy as np
import paho.mqtt.client as mqtt
import io

# MQTT Configuration
MQTT_BROKER = "<ip address of mqtt broker>"
MQTT_PORT = 1883
MQTT_USER = "<username mqtt>"
MQTT_PASSWORD = "<password mqtt>"
MQTT_TOPIC = "hanover/display"

# Hanover Display Configuration; serial port to changed to yours. Same for sign (mine at dial 1, 144x19 pixels)
ser = Serial('/dev/ttyUSB0')
controller = HanoverController(ser)
sign = HanoverSign(address=2, width=144, height=19)
controller.add_sign('office', sign)

# MQTT Client Setup
client = mqtt.Client()
if MQTT_USER and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    try:
        received_message = msg.payload.decode("utf-8")
        print(f"Received message: {received_message}")
        lines = received_message.splitlines()
        if len(lines) == 1:
            display_one_line(received_message)
        elif len(lines) >= 2:
            display_two_lines(received_message)
        else:
            print("Received empty message.")
    except UnicodeDecodeError:
        print("Error decoding MQTT message payload. Skipping display update.")

def display_one_line(text):
    """Displays one line of text using the larger font."""
    image = Image.new('1', (sign.width, sign.height), 0)
    draw = ImageDraw.Draw(image)

    font_path_big = "hanover-11x19.ttf"
    try:
        font_big = ImageFont.truetype(font_path_big, 19)
    except OSError:
        print(f"Font not found: {font_path_big}. Using default font.")
        font_big = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font_big)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (sign.width - text_width) // 2
    y = (sign.height - text_height) // 2

    draw.text((x, y), text, font=font_big, fill=1)

    sign_image = np.array(image)
    sign_image = np.where(sign_image, True, False)
    controller.draw_image(sign_image)

def display_two_lines(message):
    """Displays two lines of text using the smaller font."""
    lines = message.splitlines()
    if len(lines) > 2:
        lines = lines[:2] #only take the first two lines

    image = Image.new('1', (sign.width, sign.height), 0)
    draw = ImageDraw.Draw(image)

    font_path_6x8 = "hanover6x8.ttf"
    try:
        font_6x8 = ImageFont.truetype(font_path_6x8, 8)
    except OSError:
        print(f"Font not found: {font_path_6x8}. Using default font.")
        font_6x8 = ImageFont.load_default()

    y_offset = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_6x8)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (sign.width - text_width) // 2
        draw.text((x, y_offset), line, font=font_6x8, fill=1)
        y_offset += text_height + 2

    sign_image = np.array(image)
    sign_image = np.where(sign_image, True, False)
    controller.draw_image(sign_image)

# ... (rest of the MQTT setup, connect, loop, etc.)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the MQTT loop
client.loop_start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    client.loop_stop()
finally:
    empty_image = sign.create_image()
    controller.draw_image(empty_image)
    ser.close()