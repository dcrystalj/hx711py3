#!/usr/bin/python3
import statistics
import time
from hx711 import HX711


class Scale:
    def __init__(self, source=None, samples=20, spikes=4, sleep=0.1):

        self.source = source or HX711()
        self.samples = samples
        self.spikes = spikes
        self.sleep = sleep
        self.history = []

    def get_weight(self):
        value = self.source.get_weight()
        self.history.append(value)

        # cut to old values
        self.history = self.history[-self.samples:]

        avg = statistics.mean(self.history)
        deltas = sorted([abs(i-avg) for i in self.history])

        if len(deltas) < self.spikes:
            max_permitted_delta = deltas[-1]
        else:
            max_permitted_delta = deltas[-self.spikes]

        valid_values = list(filter(
            lambda val: abs(val - avg) <= max_permitted_delta, self.history
        ))

        avg = statistics.mean(valid_values)

        time.sleep(self.sleep)
        return avg

    def tare(self, times=25):
        self.source.tare(times)

    def set_offset(self, offset):
        self.source.set_offset(offset)

    def set_reference_unit(self, reference_unit):
        self.source.set_reference_unit(reference_unit)

    def power_down(self):
        self.source.power_down()

    def power_up(self):
        self.source.power_up()

    def reset(self):
        self.source.reset()
