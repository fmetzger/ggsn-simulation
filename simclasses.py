import logging

from simutil import *

class DurationBackend:
    def __init__(self, numberOfSupportedParallelTunnels, transientPhaseDuration):
        self.data = numpy.zeros(numberOfSupportedParallelTunnels + 1)
        self.currentTime = 0
        self.transientPhaseDuration = transientPhaseDuration

    def append(self, data):
        currentTime, numberOfProcesses, queueLength = data
        if currentTime >= self.transientPhaseDuration:
            duration = currentTime - self.currentTime
            self.currentTime = currentTime
            try:
                self.data[numberOfProcesses] += duration
            except IndexError:
                tmp = numpy.zeros(numberOfProcesses + 1 - len(self.data))
                self.data = numpy.concatenate((self.data, tmp))
                self.data[numberOfProcesses] += duration


class Users():
    def __init__(self, env, tunnelInterArrivalTimeRV, ggsn, name):
        self.env = env
        self.name = name
        self.tunnelInterArrivalTimeRV = tunnelInterArrivalTimeRV
        self.ggsn = ggsn

        self.lastNotification = 0
        self.env.start(self.run())

    def run(self):
        while True:
            currentTime = self.env.now
            if (currentTime - self.lastNotification) > 1000:
                print("Time: %f" % self.env.now)
                self.lastNotification = currentTime
            nextArrival = self.tunnelInterArrivalTimeRV(currentTime)
            yield self.env.timeout(nextArrival)
            get_logger(self.name).info("New tunnel request by user")
            self.env.start(self.ggsn.process())