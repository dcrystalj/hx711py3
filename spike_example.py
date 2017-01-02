#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import sys
import hx711

def cleanAndExit():
    print ("Cleaning...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

hx = hx711.HX711(5, 6)
samples = hx711.RollingSpikeRemoval(hx)

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
# hx.set_reference_unit(92)
samples.set_reference_unit(2100)

samples.reset()
samples.tare()

while True:
    try:
        val = samples.get_weight()

        offset = max(1,min(80,int(val+40)))
        otherOffset = 100-offset;
        print (" "*offset+"#"+" "*otherOffset+"{0: 4.4f}".format(val));

        # 
        # hx.power_down()
        # hx.power_up()
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
