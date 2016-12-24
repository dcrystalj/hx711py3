import RPi.GPIO as GPIO
import time
import numpy as np  # sudo apt-get python-np

class HX711:
    def __init__(self, dout, pd_sck, gain=128, bitsToRead=24):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)
        self.GAIN = 0
        self.REFERENCE_UNIT = 1  # The value returned by the hx711 that corresponds to your reference unit AFTER dividing by the SCALE.
        self.OFFSET = 1
        self.lastVal = 0
        self.bitsToRead = bitsToRead
        self.twosComplementThreshold = 1<<(bitsToRead-1)
        self.twosComplementOffset = -(1<<(bitsToRead))
        self.set_gain(gain)
        self.read()

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def waitForReady(self):
        while not self.is_ready():
            pass

    def correctTwosComplement(self,unsignedValue):
        if ( unsignedValue >= self.twosComplementThreshold ):
            return unsignedValue + self.twosComplementOffset
        else:
            return unsignedValue

    def read(self):
        self.waitForReady()
      
        unsignedValue = 0;
        for i in range(0,self.bitsToRead):
            GPIO.output(self.PD_SCK, True)
            bitValue = GPIO.input(self.DOUT)
            GPIO.output(self.PD_SCK, False)
            unsignedValue = unsignedValue << 1
            unsignedValue = unsignedValue | bitValue

        #set channel and gain factor for next reading
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)
        
        return self.correctTwosComplement( unsignedValue )


    def read_average(self, times=10):
        return np.average([self.read() for _ in range(times)])

    def read_average_without_bias(self, times=10, spikes=3):
        values = sorted([self.read() for _ in range(times)])

        return np.average(values[spikes:-spikes])

    def get_value(self, times=10):
        return self.read_average(times) - self.OFFSET

    def get_avg_value(self, times=20, spikes=3):
        return self.read_average_without_bias(times, spikes) - self.OFFSET

    def get_weight(self, times=10):
        value = self.get_value(times)
        value /= self.REFERENCE_UNIT
        return value

    def get_avg_weight(self, times=20, spikes=3):
        value = self.get_avg_value(times, spikes)
        value /= self.REFERENCE_UNIT
        return value

    def tare(self, times=25):
        # Backup REFERENCE_UNIT value
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = self.read_average_without_bias(times)
        self.set_offset(value)

        self.set_reference_unit(reference_unit)
        time.sleep(0.1)

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_reference_unit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    # HX711 datasheet states that setting the PDA_CLOCK pin on high for a more than 60 microseconds would power off the chip.
    # I used 100 microseconds, just in case.
    # I've found it is good practice to reset the hx711 if it wasn't used for more than a few seconds.
    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

    def reset(self):
        self.power_down()
        self.power_up()
