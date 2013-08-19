#!/usr/bin/pypy

import simpy

from simutil import *
from simclasses import *
from ggsn import Multiserver_GGSN



def main():
    (options, args) = option_parse()
    config_dict = load_config('assets/sim.config')
    for k,v in config_dict.items():
        print ("{0} = {1}".format(k,v))

    env = simpy.Environment()
    setup_logger(options, config_dict, sim_name, env)


    random.seed(options.seed)
    interarrivalRates = loadHourlyRates('assets/interarrival_rates.csv')
    tunnelInterArrivalTimeRV = lambda t: random.expovariate(tunnelInterArrivalRate(interarrivalRates, t))

    inverseCdfs = loadHourlyDuration('assets/inverse_cdf.csv')
    tunnelDurationRV = lambda t: tunnelDuration(inverseCdfs, random.uniform(0,1), t)

    ggsn = Multiserver_GGSN(env, options, config_dict)
    users = Users(env, tunnelInterArrivalTimeRV, ggsn, sim_name)

    simpy.simulate(env, until = config_dict["duration"])

    print("Writing results")
    ggsn.report(options.seed, config_dict["duration"])


if __name__ == '__main__':
    sim_name = "multiserver_ggsn"
    main()
