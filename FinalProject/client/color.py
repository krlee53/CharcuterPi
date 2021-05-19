import time
import board
import adafruit_tcs34725

# Return color that the color sensor sees
def getColor(sensor):
    # Get RGB color value
    color = sensor.color_rgb_bytes
    print("Color: ({0}, {1}, {2})".format(*color))
    return color
