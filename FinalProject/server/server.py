import socket
import struct
from move import *
from picamera import PiCamera
import subprocess

# Call sudo pigpiod
subprocess.call(['sudo', 'pigpiod'])

# Run the program
running = True

# Create the servo object
servo = Servo(19)

# Zero the servo
curr = 0
servo.write(curr)
time.sleep(2)
# Calibrate the servo
curr = drive(90, curr, servo)
time.sleep(2)
curr = drive(0, curr, servo)
time.sleep(2)
curr = drive(90, curr, servo)
time.sleep(2)
curr = drive(0, curr, servo)
time.sleep(2)

# Set up the camera and take an image
camera = PiCamera(resolution=(1280,720), framerate=30)
camera.iso = 200 # Daytime lighting
time.sleep(2)
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
camera.capture('board.jpg')
camera.close()

# Intialize distance
dist = 0

# Server loop
while running:
    # Set up socket server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('192.168.0.145',9050))
    s.listen(1)
    connection, client_address = s.accept()
    # Check for connection
    try:
        print('Connected by ', client_address)
        # Loop to receive messages
        while True:
            data = connection.recv(1024)
            data = data.decode('utf-8')
            # Check message
            if data == 'Cheese':
                print(data)
                # Move the servo to the proper position
                target_angle, curr, dist = getTargetAngle(curr, 'yellow')
                if target_angle < 400:
                    print(curr)
                    resp = 'Moving'
                    curr = drive(target_angle, curr, servo)
                else:
                    resp = 'Cannot Find'
                connection.sendall(resp.encode())
            elif data == 'Olive':
                print(data)
                # Move the servo to the proper position
                target_angle, curr, dist = getTargetAngle(curr, 'green')
                if target_angle < 400:
                    print(curr)
                    resp = 'Moving'
                    curr = drive(target_angle, curr, servo)
                else:
                    resp = 'Cannot Find'
                connection.sendall(resp.encode())
            elif data == 'Strawberry':
                print(data)
                # Move the servo to the proper position
                target_angle, curr, dist = getTargetAngle(curr, 'red')
                if target_angle < 400:
                    print(curr)
                    resp = 'Moving'
                    curr = drive(target_angle, curr, servo)
                else:
                    resp = 'Cannot Find'
                connection.sendall(resp.encode())
            elif data == 'Arrived':
                print(data)
                # Send distance
                resp = 'Moved ' + str(dist)
                connection.sendall(resp.encode())
            elif data == 'PickedUp_C':
                print(data)
                # Set up the camera and take an image
                camera = PiCamera(resolution=(1280,720), framerate=30)
                camera.iso = 200
                time.sleep(2)
                camera.shutter_speed = camera.exposure_speed
                camera.exposure_mode = 'off'
                g = camera.awb_gains
                camera.awb_mode = 'off'
                camera.awb_gains = g
                camera.capture('board.jpg')
                camera.close()
                target_angle, curr, dist = getTargetAngle(curr, 'yellow')
                # Check if food item still exists
                if target_angle < 400:
                    resp = 'Photo'
                else:
                    resp = 'None'
                connection.sendall(resp.encode())
            elif data == 'PickedUp_O':
                print(data)
                # Set up the camera and take an image
                camera = PiCamera(resolution=(1280,720), framerate=30)
                camera.iso = 200
                time.sleep(2)
                camera.shutter_speed = camera.exposure_speed
                camera.exposure_mode = 'off'
                g = camera.awb_gains
                camera.awb_mode = 'off'
                camera.awb_gains = g
                camera.capture('board.jpg')
                camera.close()
                target_angle, curr, dist = getTargetAngle(curr, 'green')
                # Check if food item still exists
                if target_angle < 400:
                    resp = 'Photo'
                else:
                    resp = 'None'
                connection.sendall(resp.encode())
            elif data == 'PickedUp_S':
                print(data)
                # Set up the camera and take an image
                camera = PiCamera(resolution=(1280,720), framerate=30)
                camera.iso = 200
                time.sleep(2)
                camera.shutter_speed = camera.exposure_speed
                camera.exposure_mode = 'off'
                g = camera.awb_gains
                camera.awb_mode = 'off'
                camera.awb_gains = g
                camera.capture('board.jpg')
                camera.close()
                target_angle, curr, dist = getTargetAngle(curr, 'red')
                # Check if food item still exists
                if target_angle < 400:
                    resp = 'Photo'
                else:
                    resp = 'None'
                connection.sendall(resp.encode())
            elif data == 'Quit':
                # Quit the program
                running = False
                curr = drive(0, curr, servo)
                resp = 'Quit'
                connection.sendall(resp.encode())
            else:
                break

    finally:
        # Close the socket
        connection.close()

# Move the table back to the intitial position
drive(0, curr, servo)
# Stop servo
servo.stop()
