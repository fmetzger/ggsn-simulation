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
import argparse
import ConfigParser
import math
import random


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

def load_config(filename):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    kv = dict()
    cfg_list = config.items("generic")
    for cfg_pair in cfg_list:
        #try:
        #    kv[cfg_pair[0]] = eval(cfg_pair[1])
        #except SyntaxError:
        #    print("invalid eval at key [{1}, {2}], using as string".format(cfg_pair))
        kv[cfg_pair[0]] = cfg_pair[1]
    return kv

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


def class_type(string):
    module_name, point, class_name = string.rpartition(".")
    module = __import__(module_name)
    return getattr(module, class_name)


def option_parse(config_dict):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--seed", type=int, default = config_dict["seed"])

    parser.add_argument("-c", "--logToConsole", action="store_true")
    parser.add_argument("-f", "--logToFile", action="store_true", default=True)
    parser.add_argument("-l", "--logLevel", default="WARN")

    parser.add_argument("-t", "--transientPhaseDuration", type=int, default = config_dict["transient_phase_duration"])
    parser.add_argument("-d", "--duration", type=int, default = config_dict["duration"])

    parser.add_argument("-n", "--numberOfSupportedParallelTunnels", type=int, default = config_dict["number_of_supported_parallel_tunnels"])

    subparsers = parser.add_subparsers(title = "type", description = "available ggsn types", dest="type")
    traditional_parser = subparsers.add_parser("traditional")

    multiserver_parser = subparsers.add_parser("multiserver")
    multiserver_parser.add_argument("-u", "--startupTime", type=int, default = 20)
    multiserver_parser.add_argument("-z", "--shutdownTime", type=int, default = 20)
    multiserver_parser.add_argument("-U", "--startupCondition", type=class_type, default = config_dict["startup_condition"])
    multiserver_parser.add_argument("-Z", "--shutdownCondition", type=class_type, default = config_dict["shutdown_condition"])

    # parser.add_option("-l", "--shutdownCondition", type="string", help="Condition under which to shut down an instance, expression as three variable lambda: tunnels, instances, instancecapacity")
    result = parser.parse_args()


    return result


def setup_logger(options, env):
    simulationFormatter = SimulationFormatter(env)
    logger = logging.getLogger(options.type)
    if options.logLevel == "INFO":
        logger.setLevel(logging.INFO)
    elif options.logLevel == "WARN":
        logger.setLevel(logging.WARN)
    else:
        logger.setLevel(logging.WARN)


    if options.logToFile:
        fileHandler = logging.FileHandler("%s_%d_%d_%d.log" % (options.type, options.numberOfSupportedParallelTunnels, options.duration, options.seed))
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
