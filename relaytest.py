#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO

"""
The pin numbers refer to the board connector not the chip
"""
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, GPIO.HIGH)

print(" Control + C to exit Program")

try:
    while 1 >= 0:
        GPIO.output(7, GPIO.LOW)   # turns the first relay switch ON
        time.sleep(.5)             # pauses system for 1/2 second
        GPIO.output(7, GPIO.HIGH)  # turns the first relay switch OFF
        GPIO.output(11, GPIO.LOW)  # turns the second relay switch ON
        time.sleep(.5)
        GPIO.output(11, GPIO.HIGH)
except KeyboardInterrupt:     # Stops program when "Control + C" is entered
    GPIO.cleanup()            # Turns OFF all relay switches
