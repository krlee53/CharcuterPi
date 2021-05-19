import socket
import pygame
from pygame.locals import*
import os
import RPi.GPIO as GPIO
from color import *
import subprocess
from arm import *
import pigpio

# Call pigpiod
subprocess.call(['sudo', 'pigpiod'])

# Set up environment
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# Use BCM numbers
GPIO.setmode(GPIO.BCM)

# Initialize pygame
pygame.init()
pygame.mouse.set_visible(False)

# Set up GPIO pins
GPIO.setup(12, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize duty cycle
dutyA = 100
dutyB = 100

# Set up DC motors
GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
p = GPIO.PWM(12, 50)
p.start(dutyA)

GPIO.output(26, GPIO.LOW)
GPIO.output(19, GPIO.LOW)
q = GPIO.PWM(21, 50)
q.start(dutyB)

# Set up servo motors
left_pin = 13
right_pin = 12

left = pigpio.pi()
left.set_mode(left_pin, pigpio.OUTPUT)

right = pigpio.pi()
right.set_mode(right_pin, pigpio.OUTPUT)

# Define colors
black = 0,0,0
white = 255,255,255
red = 255,0,0
green = 0,255,0
yellow = 255,255,0

# Define button dictionary
buttons = {'Cheese': (250,50), 'Olive': (250,100), 'Strawberry': (250,150), 'Quit': (250,200)}

screen = pygame.display.set_mode((320, 240))

font = pygame.font.Font(None, 20)

# Server IP and port
ip = '192.168.0.145'
port = 9050

# Set up color sensor
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.gain = 16
color = (255,255,255)

# Run the program
running = True
sendData = False
data = ''

# Variables to keep track of existing foods
cheese = True
olive = True
strawberry = True

# Initialize the clock
clock = pygame.time.Clock()

# Assign buttons to rects and text surfaces
for text, text_pos in buttons.items():
    text_surface = font.render(text, True, white)
    rect = text_surface.get_rect(center=text_pos)
    if text == 'Cheese':
        rect1 = rect
        text_surface1 = text_surface
    elif text == 'Olive':
        rect2 = rect
        text_surface2 = text_surface
    elif text == 'Strawberry':
        rect3 = rect
        text_surface3 = text_surface
    elif text == 'Quit':
        rect4 = rect
        text_surface4 = text_surface

# GPIO17 callback function
def GPIO17_callback(channel):
    global sendData
    global data
    global cheese
    # Send cheese
    if cheese:
        sendData = True
        data = 'Cheese'

# GPIO22 callback function
def GPIO22_callback(channel):
    global sendData
    global data
    global olive
    # Send olive
    if olive:
        sendData = True
        data = 'Olive'

# GPIO23 callback function
def GPIO23_callback(channel):
    global sendData
    global data
    global strawberry
    # Send strawberry
    if strawberry:
        sendData = True
        data = 'Strawberry'

# Physical quit button
def GPIO27_callback(channel):
    global sendData
    global data
    global running
    # Quit the program on both ends
    running = False
    sendData = True
    data = 'Quit'

# Add GPIO events
GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300)
GPIO.add_event_detect(22, GPIO.FALLING, callback=GPIO22_callback, bouncetime=300)
GPIO.add_event_detect(23, GPIO.FALLING, callback=GPIO23_callback, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300)

# Drive function
def drive(direction):
    if direction == 'forward':
        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        GPIO.output(6, GPIO.HIGH)
    elif direction == 'backward':
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(19, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.LOW)
    elif direction == 'stop':
        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
        GPIO.output(6, GPIO.LOW)

# Run program
while running:
    # Set FPS
    clock.tick(40)
    
    # Clear the screen
    screen.fill(black)

    # Display buttons
    if cheese:
        # Display cheese button
        screen.blit(text_surface1, rect1)
    if olive:
        # Display olive button
        screen.blit(text_surface2, rect2)
    if strawberry:
        # Disply strawberry button
        screen.blit(text_surface3, rect3)

    # Display quit button
    screen.blit(text_surface4, rect4)
    
    # Check if should send message to server
    if sendData:
        print(data)
        sendData = False
        try:
            # Connect to server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            msg = data
            # Send message to server
            s.sendall(msg.encode())
            resp = s.recv(1024)
            resp = resp.decode('utf-8')
            print(resp)
            # Check server response
            if resp == 'Moving':
                # Move robot off starting line
                drive('forward')
                time.sleep(2)
                color = getColor(sensor)
                while (color[0] < 50 and color[1] < 180 and color[2] <= 255 and color[0] > 0 and color[1] > 0 and color[2] > 125):
                    # Move the robot forward off the start line
                    drive('forward')
                    # Check color
                    color = getColor(sensor)
                # Check that the robot is not on the blue line
                while not (color[0] < 50 and color[1] < 180 and color[2] <= 255 and color[0] > 0 and color[1] > 0 and color[2] > 125):
                    color = getColor(sensor)
                    drive('forward')
                drive('stop')
                # Tell server that robot has arrived
                msg = 'Arrived'
                s.sendall(msg.encode())
                resp = s.recv(1024)
                resp = resp.decode('utf-8')
                print(resp)
                resp = resp.split(' ')
                if resp[0] == 'Moved':
                    dist = resp[1]
                    # Robot arm movement
                    arm(dist, left, right)
                    # Send response based on what robot picked up
                    if data == 'Cheese':
                        msg = 'PickedUp_C'
                        s.sendall(msg.encode())
                    elif data == 'Olive':
                        msg = 'PickedUp_O'
                        s.sendall(msg.encode())
                    elif data == 'Strawberry':
                        msg = 'PickedUp_S'
                        s.sendall(msg.encode())
                    # Drive off of the end line
                    while (color[0] < 50 and color[1] < 180 and color[2] <= 255 and color[0] > 0 and color[1] > 0 and color[2] > 125):
                        drive('backward')
                        # Check color
                        color = getColor(sensor)
                    resp = s.recv(1024)
                    resp = resp.decode('utf-8')
                    print(resp)
                    # Check if should remove option from GUI
                    if resp == 'None':
                        if data == 'Cheese':
                            cheese = False
                        elif data == 'Olive':
                            olive = False
                        elif data == 'Strawberry':
                            strawberry = False
                    # Move backward until reach start again
                    while not (color[0] < 50 and color[1] < 180 and color[2] <= 255 and color[0] > 0 and color[1] > 0 and color[2] > 125):
                        color = getColor(sensor)
                        drive('backward')
                    drive('stop')
        finally:
            # Close connection
            s.close()

    # Display GUI
    pygame.display.flip()

# Stop motors
p.stop()
q.stop()
left.stop()
right.stop()
# Cleanup GPIO pins
GPIO.cleanup()
