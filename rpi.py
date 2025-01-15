from pyflipdot.pyflipdot import HanoverController
from pyflipdot.sign import HanoverSign
from serial import Serial
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import time
import numpy as np
import paho.mqtt.client as mqtt

# MQTT Configuration to be adapted
MQTT_BROKER = "<ip address mqtt broker>"
MQTT_PORT = 1883
MQTT_USER = "<username mqtt>"
MQTT_PASSWORD = "<password mqtt>"
MQTT_TOPIC = "hanover/display"

# Hanover Display Configuration to be replaced by your own sign
ser = Serial('/dev/ttyUSB0')
controller = HanoverController(ser)
sign = HanoverSign(address=2, width=144, height=19)
controller.add_sign('office', sign)

# Font paths
BIG_FONT_PATH = "hanover11x19.ttf"
SMALL_FONT_PATH = "hanover6x8.ttf"

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

        if received_message.startswith("image:"):
            # Extract image file path (e.g., 'image:picture.jpg')
            image_path = received_message.split(":", 1)[1].strip()
            if os.path.exists(image_path):
                graphic_image = handle_graphic_image(image_path)
                display_graphic_image(graphic_image)
            else:
                print(f"Image not found: {image_path}")
        elif received_message.startswith("<") and ">" in received_message:
            # Handle image/icon path
            icon_path = received_message[1:received_message.index(">")]
            text = received_message[received_message.index(">") + 1:].strip()
            display_icon_and_text(icon_path, text)
        else:
            # Handle emojis and plain text
            display_text_with_emoji(received_message)
    except Exception as e:
        print(f"Error processing message: {e}")

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        print(f"Font not found: {path}. Using default font.")
        return ImageFont.load_default()

def handle_graphic_image(image_path):
    """Handles the conversion of an image to fit the display, scale it to 19px high, and invert it."""
    # Load the image
    image = Image.open(image_path)
    
    # Scale the image to 19px high, keeping aspect ratio
    aspect_ratio = image.width / image.height
    new_width = int(19 * aspect_ratio)  # New width based on 19px height
    
    # If the new width is less than the sign width, pad the image to fit the sign width
    if new_width < sign.width:
        image = image.resize((new_width, 19), Image.Resampling.LANCZOS)
        # Create a new black image of size 144x19 to hold the resized image
        new_image = Image.new('1', (sign.width, sign.height), 0)  # 0 for black background
        new_image.paste(image, ((sign.width - new_width) // 2, 0))  # Center the image
        image = new_image
    else:
        # Ensure the image fills the full width (144px) by stretching it horizontally
        image = image.resize((sign.width, 19), Image.Resampling.LANCZOS)
    
    # Convert the image to 1-bit black and white
    image = image.convert('1')  
    
    # Invert the image (for black/white display)
    image = ImageOps.invert(image)

    # Check if image size is compatible with sign dimensions (144x19)
    if image.width != sign.width or image.height != sign.height:
        print(f"Error: Image size {image.width}x{image.height} is incompatible with sign size {sign.width}x{sign.height}.")
        return None
    
    return image


def display_graphic_image(image):
    """Display the graphic image on the Hanover sign."""
    if image is None:
        return
    sign_image = np.array(image)
    sign_image = np.where(sign_image, True, False)
    controller.draw_image(sign_image)

def display_icon_and_text(icon_path, text):
    """Displays an icon and text on the display, adjusting font size and handling long text."""
    image = Image.new('1', (sign.width, sign.height), 0)
    draw = ImageDraw.Draw(image)

    # Load and resize the icon
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert('1')
        icon = icon.resize((19, 19), Image.Resampling.LANCZOS)
        icon = ImageOps.invert(icon)  # Invert the icon
        image.paste(icon, (0, 0))
    else:
        print(f"Icon not found: {icon_path}. Displaying text only.")
        display_text_with_emoji(text)  # Fallback to text-only display
        return

    # Render remaining text with emojis, adjusted for length
    display_text_with_emoji(text, image=image, x_offset=20)

def display_text_with_emoji(text, image=None, x_offset=0):
    """Converts text with emojis into an image and displays it. Adjusts text to two lines if too long."""
    if image is None:
        image = Image.new('1', (sign.width, sign.height), 0)
    draw = ImageDraw.Draw(image)

    while "[" in text and "]" in text:
        # Extract the emoji name
        start = text.index("[")
        end = text.index("]")
        emoji_name = text[start + 1:end]

        # Display the emoji if it exists
        icon_path = f"emoji_icons/{emoji_name}.bmp"
        if os.path.exists(icon_path):
            emoji_icon = Image.open(icon_path).convert('1')
            emoji_icon = emoji_icon.resize((19, 19), Image.Resampling.LANCZOS)
            emoji_icon = ImageOps.invert(emoji_icon)  # Invert the emoji
            image.paste(emoji_icon, (x_offset, 0))
            x_offset += 20
        else:
            print(f"Emoji not found: {emoji_name}")

        # Remove the processed emoji tag
        text = text[end + 1:].strip()

    # Determine whether text fits in one line or needs two lines
    font_big = load_font(BIG_FONT_PATH, 19)
    font_small = load_font(SMALL_FONT_PATH, 8)
    
    # Get the bounding box of the text using textbbox() instead of textsize()
    bbox = draw.textbbox((0, 0), text, font=font_big)
    text_width = bbox[2] - bbox[0]  # width of the text

    if x_offset + text_width > sign.width:  # Too long for one line
        lines = []
        words = text.split()
        current_line = ""

        for word in words:
            # Calculate the width of the current line with the new word
            line_bbox = draw.textbbox((0, 0), current_line + " " + word, font=font_small)
            line_width = line_bbox[2] - line_bbox[0]
            
            if line_width <= sign.width - x_offset:
                current_line += " " + word if current_line else word
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        y_offset = 0
        for line in lines[:2]:  # Display up to two lines
            draw.text((x_offset, y_offset), line, font=font_small, fill=1)
            y_offset += 10
    else:  # Fits in one line
        draw.text((x_offset, 0), text, font=font_big, fill=1)

    sign_image = np.array(image)
    sign_image = np.where(sign_image, True, False)
    controller.draw_image(sign_image)

# Set MQTT callbacks
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
    controller
