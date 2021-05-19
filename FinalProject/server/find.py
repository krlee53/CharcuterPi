import cv2
from picamera import PiCamera
import numpy as np
import time
from fractions import Fraction
import math
from piservo import Servo
import time

# This function will take a vector and compute the angle required
# to align it with the positive y axis. It is assumed that the input
# vector is relative to the middle of the table.
# This function also takes the current angle of the servo relative
# to its zero position
def computeAngle(x, y, curr_angle):
    # FIRST QUADRANT
    phi = curr_angle*360/174 # Set phi to the current angle
    print("X: " + str(x))
    print("Y: " + str(y))
    if (x >= 0 and y < 0):
        print("First Quadrant")
        theta = -math.atan(x/y) * (180/math.pi)
        if phi < theta:
            target_angle = 360 - (theta - phi)
        else:
            target_angle = phi - theta
        print(target_angle)

    # SECOND QUADRANT
    elif (x >= 0 and y >= 0):
        print("Second Quadrant")
        theta = math.atan(y/x) * (180/math.pi)
        if phi < (90 + theta):
            target_angle = 360 - ((90 + theta) - phi)
        else:
            target_angle = phi - (90 + theta)
        print(target_angle)

    # THIRD QUADRANT
    elif (x < 0 and y >= 0):
        print("Third Quadrant")
        theta = -math.atan(x/y) * (180/math.pi)
        if phi < (180 + theta):
            target_angle = 360 - ((180 + theta) - phi)
        else:
            target_angle = phi - (180 + theta)
        print(target_angle)

    # FOURTH QUADRANT
    elif (x < 0 and y < 0):
        print("Fourth Quadrant")
        theta = math.atan(y/x) * (180/math.pi)
        if phi < (270 + theta):
            target_angle = 360 - ((270 + theta) - phi)
        else:
            target_angle = phi - (270 + theta)
        print(target_angle)

    else:
        print("Couldn't Find Quadrant")

    # Return the angle to move to
    return target_angle
