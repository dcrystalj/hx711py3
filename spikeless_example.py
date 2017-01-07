#!/usr/bin/python3
import sys
import RPi.GPIO as GPIO
from scale import Scale

scale = Scale()

scale.setReferenceUnit(21)

scale.reset()
scale.tare()

while True:

    try:
        val = scale.getMeasure()
        print("{0: 4.4f}".format(val))

    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        sys.exit()
