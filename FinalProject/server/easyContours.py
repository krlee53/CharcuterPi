from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random
import time
from picamera import PiCamera

# Function used for testing. Displays all images
def easyContoursImage(original, masked, thresh):
    # Apply a blur to the masked image
    src_gray = cv.blur(masked, (2, 2))

    blur_window = 'Blur'
    cv.namedWindow(blur_window)
    cv.imshow(blur_window, src_gray)

    # Find edges
    canny_output = cv.Canny(src_gray, thresh, thresh * 2)

    # Find contours
    contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    contours_poly = [None]*len(contours)
    boundRect = []
    centers = []
    radius = []
    # Draw rectangles around contours
    for i, c in enumerate(contours):
        contours_poly[i] = cv.approxPolyDP(c, 3, True)
        x,y,w,h = cv.boundingRect(contours_poly[i])
        # Check if the contour has a large enough area
        if w > 25 and h > 25:
            boundRect.append([x,y,w,h])
            center, radius = cv.minEnclosingCircle(contours_poly[i])
            centers.append(center)
    # Display rectangles on original image
    for rectangle in boundRect:
        color = (random.randint(0,256), random.randint(0,256), random.randint(0,256))
        cv.rectangle(original, (int(rectangle[0]), int(rectangle[1])), \
                (int(rectangle[0]+rectangle[2]), int(rectangle[1]+rectangle[3])), color, 2)

    return original

# Function called to get the contours around the masked image
def easyContours(masked, thresh):
    # Apply a blur to the image
    src_gray = cv.blur(masked, (2, 2))

    # Find edges
    canny_output = cv.Canny(src_gray, thresh, thresh * 2)

    # Find contours
    contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    contours_poly = [None]*len(contours)
    boundRect = []
    centers = []
    # Draw rectangles around contours
    for i, c in enumerate(contours):
        contours_poly[i] = cv.approxPolyDP(c, 3, True)
        x,y,w,h = cv.boundingRect(contours_poly[i])
        # Check if the contour has a large enough area
        if w > 25 and h > 25:
            boundRect.append([x,y,w,h])
            center, radius = cv.minEnclosingCircle(contours_poly[i])
            centers.append(center)

    # Return a list of centers of rectangles
    return centers
