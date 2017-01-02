import RPi.GPIO as GPIO
import time

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

    def get_value(self):
        return self.read() - self.OFFSET

    def get_weight(self):
        value = self.get_value()
        value /= self.REFERENCE_UNIT
        return value

    def tare(self, times=25):
        # Backup REFERENCE_UNIT value
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = 0
        for i in range(times):
          value += self.read()
        self.set_offset(value/times)

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

class RollingSpikeRemoval:
    def __init__(self, source, samples=10, spikes=2):
        self.source = source
        self.samples = samples
        self.spikes = spikes
        self.history = [];

    def get_weight(self):
        value = self.source.get_weight()
        self.history.append( value )
        if ( len(self.history) > self.samples ):
            self.history = self.history[1:]
        average = sum( self.history ) / len(self.history)
        deltas = sorted( map( lambda value: abs(value - average) , self.history ) )
        if ( len(deltas) < self.spikes ):
          maxPermittedDelta = deltas[-1]
        else:
          maxPermittedDelta = deltas[-self.spikes]
        validValues = sorted(filter( lambda value: abs(value-average) <= maxPermittedDelta , self.history ))
        average = sum(validValues)/len(validValues)
        return average

    def tare(self, times=25):
        self.source.tare(times)

    def set_offset(self, offset):
        self.source.set_offset(offset)

    def set_reference_unit(self, reference_unit):
        self.source.set_reference_unit( reference_unit)

    def power_down(self):
        self.source.power_down()

    def power_up(self):
        self.source.power_up()

    def reset(self):
        self.source.reset()
