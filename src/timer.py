from ursina import *

class Timer:
    def __init__(self, timeout, counts, tick_callback, end_callback):
        self.timeout = timeout
        self.timer = 0
        self.counts_limit = counts
        self.ticks_count = 0
        self.tick_callback = tick_callback
        self.end_callback = end_callback
        self.is_on = False
        self.effect = 0

    def update(self):
        if not self.is_on:
            return
        
        self.timer += time.dt
        if self.timeout < self.timer:
            self.tick_callback(self.effect)
            self.ticks_count += 1
            if self.counts_limit <= self.ticks_count:
                self.end_callback()
                self.stop()

            self.timer = 0

    def start(self, effect=None):
        if self.is_on:
            return
        self.effect = effect
        self.is_on = True
        self.timer = 0
        self.ticks_count = 1
        self.tick_callback(self.effect)

    def stop(self):
        self.is_on = False
        self.timer = 0
        self.ticks_count = 0
