import cv2 as cv
import numpy as np
from fractions import Fraction
import math
from piservo import Servo
import time
from find import *
from easyContours import *
import random

# Function to slowly drive servo to a position
def drive(angle, curr_angle, servo):
    # Normalize to account for angle inaccuracy
    normalize = 172/180
    angle = angle * normalize
    while curr_angle < angle:
        curr_angle += 1
        servo.write(curr_angle)
        time.sleep(0.05)
    while curr_angle > angle:
        curr_angle -= 1
        servo.write(curr_angle)
        time.sleep(0.05)
    return curr_angle

# Function used for testing. Displays images
def getTargetAngleImage(curr_angle, color):
    frame = cv.imread('photo.jpg')

    # Define color thresholds
    lower_red = np.array([165, 100, 90])
    upper_red = np.array([179, 255, 255])

    lower_yellow = np.array([0,100, 150])
    upper_yellow = np.array([20, 255, 255])

    lower_green = np.array([15, 50, 30])
    upper_green = np.array([50, 255, 150])

    # Convert the image to HSV and apply the color mask
    # to find the sponge 
    frame1 = cv.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if color == 'red':
        spongeFrame = cv.inRange(frame1, lower_red, upper_red)
    elif color == 'yellow':
        spongeFrame = cv.inRange(frame1, lower_yellow, upper_yellow)
    elif color == 'green':
        spongeFrame = cv.inRange(frame1, lower_green, upper_green)

    # Get the contours from the sponges (should give the center
    # of the sponges)
    try:
        sponges = easyContours(spongeFrame, 190)
        assert len(sponges) > 0, "No Sponges Found!"
    except AssertionError:
        # Display the sponge mask
        cv.imshow('Sponge Mask', spongeFrame)

        while True:
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    origin_x = 633
    origin_y = 332

    # Pick a sponge at random
    chosenSponge = sponges[random.randint(0, len(sponges)-1)]
    sx, sy = chosenSponge

    # Calculate the vector for the sponge
    x = sx - origin_x
    y = sy - origin_y

    # Get the angle we need to move to to align the chosen sponge
    # with the positive y axis
    target_angle = computeAngle(x, y, curr_angle) / 2
    dist = x**2 + y**2
    dist = math.sqrt(dist)


    # Draw the bounding rectangles on the original image
    frame = easyContoursImage(frame, spongeFrame, 190)

    # Also going to draw axis through the origin on the image for clarity
    cv.line(frame, (1280, int(origin_y)), (0, int(origin_y)), (255, 255, 255), 2)
    cv.line(frame, (int(origin_x), 0), (int(origin_x), 720), (255, 255, 255), 2)


    # Display the original, annotated image
    cv.imshow('frame',frame)

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # Display the original, annotated image
    cv.imshow('Sponge Frame',spongeFrame)

    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()

    # Return the angle
    return target_angle, curr_angle, dist

# Function to find the target angle and distance to the food
def getTargetAngle(curr_angle, color):
    # Load table image
    frame = cv.imread('board.jpg')

    # Initialize distance and target angle
    dist = 0
    target_angle = 0
    
    # Define color thresholds
    lower_red = np.array([165, 100, 90])
    upper_red = np.array([179, 255, 255])

    lower_yellow = np.array([0,100, 150])
    upper_yellow = np.array([20, 255, 255])

    lower_green = np.array([15, 50, 30])
    upper_green = np.array([50, 255, 150])

    # Convert the image to HSV and apply the color mask
    # to find the food 
    frame1 = cv.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if color == 'red':
        foodFrame = cv.inRange(frame1, lower_red, upper_red)
    elif color == 'yellow':
        foodFrame = cv.inRange(frame1, lower_yellow, upper_yellow)
    elif color == 'green':
        foodFrame = cv.inRange(frame1, lower_green, upper_green)

    # Get the contours from the food (should give the center
    # of the food)
    try:
        food = easyContours(foodFrame, 190)
        assert len(food) > 0, "No Food Found!"
    except AssertionError:
        target_angle = 400

    # Check that food has been found
    if target_angle == 0:

        # Center of table
        origin_x = 633
        origin_y = 332

        # Pick a sponge at random
        chosenFood = food[random.randint(0, len(food)-1)]
        sx, sy = chosenFood

        # Calculate the vector for the food
        x = sx - origin_x
        y = sy - origin_y

        # Get the angle we need to move to to align the chosen food
        # with the positive y axis
        target_angle = computeAngle(x, y, curr_angle) / 2

        # Calculate the distance from the center of the food to the center of the table
        dist = math.sqrt(x**2 + y**2)

    # Return the angle
    return target_angle, curr_angle, dist
