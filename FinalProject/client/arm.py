# 
# gtz4, kjl92
# arm.py
# controls arm servos
#

import time
import RPi.GPIO as GPIO
import pigpio
import math

def arm(pixels_to_c, left, right):

    # home position, should be in this before this function is called
    home_bicep = 20 #10
    last_bicep = home_bicep
    home_forearm = 45 #70
    last_forearm = home_forearm

    table_d = 15.5 # cm
    table_p = 741 # pixels

    conversion = table_d/table_p # cm/pixels

    x = 15 - (int(float(pixels_to_c)) - 5)*conversion
    y1 = 3 #5
    y2 = -1

    # go from home position to hover above food
    print('Home -> Hover')
    forearm, bicep = calculate_angles(x, y1)
    last_forearm, last_bicep = move_arm(bicep, forearm, last_bicep, last_forearm, left, right)
    time.sleep(2)

    # go from hover position to stab food
    print('Hover -> Stab')
    forearm, bicep = calculate_angles(x, y2)
    last_forearm, last_bicep = move_arm(bicep, forearm, last_bicep, last_forearm, left, right)
    time.sleep(2)

    # go from stab position to hover 
    print('Stab -> Hover')
    forearm, bicep = calculate_angles(x, y1)
    last_forearm, last_bicep = move_arm(bicep, forearm, last_bicep, last_forearm, left, right)
    time.sleep(2)

    # go from hover back to home position
    print('Hover -> Home')
    move_arm(home_bicep, home_forearm, last_bicep, last_forearm, left, right)
    


def calculate_angles(x,y):
    import math

    b = math.sqrt(x**2 + y**2)
    a = 8
    c = 8
    D = math.degrees(math.atan(y/x))

    # law of cosines
    # a^2 = b^2 + c^2 -2*b*c*cosA
    B = math.acos((b**2 - a**2 - c**2)/(-2*a*c))
    A = math.acos((a**2 - b**2 - c**2)/(-2*b*c))
    B = math.degrees(B)
    A = math.degrees(A)
    C = 180 - A - B
    D = abs(D)

#   print('A: ')
#   print(A)
#   print('B: ')
#   print(B)
#   print('C: ')
#   print(C)
#   print('D: ')
#   print(D)

    # convert to servo values
    if (y > 0):
        bicep = int((90 - A - D)/1.05)
        forearm = int((B - 90 + A + D)/1.05)
    elif (y == 0):
        bicep = int((90 - A)/1.05)
        forearm = int((B/2)/1.05)
    else:
        bicep = int((90 - A + D)/1.05)
        forearm = int((90 - D - C)/1.05)

    if forearm > 80:
        forearm = 80
    if forearm < 10:
        forearm = 10
    if bicep > 80:
        bicep = 80
    if bicep < 10:
        bicep = 10
   
    print('bicep angle: ')
    print(bicep)
    print('forearm angle: ')
    print(forearm)

    return forearm, bicep

def move_arm(bicep, forearm, last_bicep, last_forearm, left, right):

    left_pin = 13
    right_pin = 12

    i = last_bicep
    j = last_forearm

    direction_left = bicep - last_bicep
    direction_right = forearm - last_forearm

    while ((i != bicep) or (j != forearm)):
        if j!= forearm:
            f = int((j*2000/180 + 500) * 50)
            left.hardware_PWM(13, 50, f)
            #print('Left angle: ')
            #print(j)
            time.sleep(0.05)
            if direction_right > 0:
                j = j + 1
            else:
                j = j - 1
        if i!= bicep:
            b = int((i*2000/180 + 500) * 50)
            right.hardware_PWM(12, 50, b)
            #print('Right angle: ')
            #print(i)
#            time.sleep(0.005)
            if direction_left > 0:
                i = i + 1
            else:
                i = i - 1

#   f = int((forearm*2000/180 + 500) * 50)
#   left.hardware_PWM(left_pin, 50, f)
#   time.sleep(0.1)
#   b = int((bicep*2000/180 + 500) * 50)
#   right.hardware_PWM(right_pin, 50, b)
#   time.sleep(0.1)
#       
    last_bicep = bicep
    last_forearm = forearm

    left.set_PWM_dutycycle(left_pin, 0)
    left.set_PWM_frequency(left_pin, 0)
    right.set_PWM_dutycycle(right_pin, 0)
    right.set_PWM_frequency(right_pin, 0)

    return last_forearm, last_bicep
   
