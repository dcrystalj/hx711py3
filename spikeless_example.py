#!/usr/bin/python3
import sys
import RPi.GPIO as GPIO
from scale import Scale

scale = Scale()

scale.set_reference_unit(21)

scale.reset()
scale.tare()

while True:

    try:

        val = scale.get_weight()

        print("{0: 4.4f}".format(val))

    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        sys.exit()
