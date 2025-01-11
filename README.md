# hanover-led-display
Show all kind of data or pictures on a Hanover LED display via RS485

Since time ago I bought a Hanover display (that was meant to be used as a bus display). I also have a flipdot bus display, but this one is the LED version.

Some more details about my setup:
- Resolution: 144x19 pixels (amber leds)
- Address: when you open the display at the back, you can see the motherboard and there are normally dials on it to set the address. Mine was having dipswitches. Set mine to 1 (which means later on that the address will be 2, as 1 is to be added)
- Looked at many repositories, but the one that worked for me was the pyflipdot-0.2.2
- Bought a RS485 USB connector (mine was a version with a long cable and crocodile clips)
- On my pc I installed the latest version of Python (3.13.1)
- Some Python modules that I installed to get this working (pip, numpy, paho-mqtt, pillow, pyflipdot, pyserial, smmap)

I first connected the red and black communication cables that came out of the Hanover to the USB485 adapter (red to red, black to black). Furthermore, the LED display itself must be connected to the power supply (mine 24V - 2A).

Then it's time to start the display via several python codes:
- First is a simple text (hantext.py), where text is converted to an image. This requires a font to be loaded (I downloaded the hanover-11x19.ttf font, because it fitted easily with my display).
- Second code is a mqtt client version. This let the screen be updated when a new message arrives in the MQTT server. I use that mostly to link to my Home Assistant MQTT broker, where I can easily include sensor-data. An example sent from Home Assistant: payload: "Water: {{ ((states('sensor.water_dagelijks_verbruik') | default(0)) | float * 1000) | round(0) }}L"
- Third one is the conversion of a picture. I used a black and white picture of a skyline, which was visually only very roughly like the dimensions of the Hanover display. The picture (skyline.jpg) was 628x194 pixels. This is then converted to the 144x19 dimensions. 
![Source picture](skyline.jpg)
![After][skylineafter.jpg)
