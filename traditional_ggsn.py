#!/usr/bin/pypy

import simpy

from simutil import *
from simclasses import *
from ggsn import Traditional_GGSN


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

    # inverseTunnelDurationCdf = lambda x: 3.8147e-6 / (x - 1) * (2.55328e8 - 4.20317e8 * x - math.sqrt(6.51925e16 - 2.06182e17 * x + 1.68178e17 * x**2) )
    # tunnelDurationRV = inversionMethod(inverseTunnelDurationCdf)

    # inverseCdfs = loadHourlyDuration('assets/inverse_cdf.csv')
    # tunnelDurationRV = lambda t: tunnelDuration(inverseCdfs, random.uniform(0,1), t)

    ggsn = Traditional_GGSN(env, options, config_dict)
    users = Users(env, tunnelInterArrivalTimeRV, ggsn, sim_name)

    simpy.simulate(env, until = config_dict["duration"])

    print("Writing results")
    ggsn.report(options.seed, config_dict["duration"])


if __name__ == '__main__':
    sim_name = "traditional_ggsn"
    main()