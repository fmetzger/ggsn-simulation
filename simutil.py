import logging
import csv
import os
import errno
import sys
is_pypy = '__pypy__' in sys.builtin_module_names
if is_pypy:
    import numpypy
import numpy
import logging
import optparse
import math
import random

#from simclasses import *

#def each_cons(x, n):
#    return [x[i:i+n] for i in range(len(x) - n + 1)]



def inversionMethod(inverseCdf):
    return lambda: inverseCdf(random.random())

def loadHourlyRates(filename):
    rates = []
    with open(filename) as csvFile:
        reader = csv.DictReader(csvFile, delimiter = ";")
        for row in reader:
            rates.append(float(row.get("rates")))

    #return rates
    return [rate/max(rates) for rate in rates]


def loadHourlyDuration(filename):
    inverseCdf = []
    with open(filename) as csvFile:
        reader = csv.DictReader(csvFile, delimiter = ";")
        for row in reader:
            inverseCdf.append(eval(row.get("icdf")))

    return inverseCdf

def getHourOfTheDay(t):
    secondOfDay = t % (60 * 60 * 24)
    return int(math.floor(secondOfDay / (60 * 60)))


def tunnelInterArrivalRate(interarrivalRates, t):
    hour = getHourOfTheDay(t)
    return interarrivalRates[hour]


def tunnelDuration(inverseCdfs, rvar, t):
    hour = getHourOfTheDay(t)
    icdf = inverseCdfs[hour]
    return icdf(rvar)

def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def get_logger(loggername):
    return logging.getLogger(loggername)


def option_parse():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--seed", type="int", default = 13)
    parser.add_option("-n", "--numberOfSupportedParallelTunnels", type="int", default = 2)
    parser.add_option("-d", "--duration", type="int", default = 48)
    parser.add_option("-c", "--logToConsole", action="store_true")
    parser.add_option("-f", "--logToFile", action="store_true", default=True)
    parser.add_option("-t", "--transientPhaseDuration", type="int", default = 3600)
    parser.add_option("-u", "--startupTime", type="int", default = 20)
    parser.add_option("-z", "--shutdownTime", type="int", default = 20)
    parser.add_option("-l", "--shutdownCondition", type="string", help="Condition under which to shut down an instance, expression as three variable lambda: tunnels, instances, instancecapacity")

    return parser.parse_args()


def setup_logger(options, name, env):
    simulationFormatter = SimulationFormatter(env)
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARN)
    if options.logToFile:
        fileHandler = logging.FileHandler("%s_%d_%d_%d.log" % (name, options.numberOfSupportedParallelTunnels, options.duration, options.seed))
        fileHandler.setFormatter(simulationFormatter)
        logger.addHandler(fileHandler)
    if options.logToConsole:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(simulationFormatter)
        logger.addHandler(consoleHandler)


class SimulationFormatter(logging.Formatter):
    def __init__(self, env):
        self.env = env
        super(SimulationFormatter, self).__init__()

    def format(self, record):
        record.msg = '%f: %s' % (self.env.now, record.msg)
        return super(SimulationFormatter, self).format(record)
