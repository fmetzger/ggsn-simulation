#!/usr/bin/pypy

import simpy

from simutil import *
from simclasses import *
from ggsn import Traditional_GGSN


def main():
    (options, args) = option_parse()
    env = simpy.Environment()
    setup_logger(options, sim_name, env)

    print("Simulating for %d seconds (transient phase of %d seconds) with a support for %d parallel tunnels and seed %d." % (options.duration, options.transientPhaseDuration, options.numberOfSupportedParallelTunnels, options.seed))

    random.seed(options.seed)
    interarrivalRates = loadHourlyRates('assets/interarrival_rates.csv')
    tunnelInterArrivalTimeRV = lambda t: random.expovariate(tunnelInterArrivalRate(interarrivalRates, t))

    inverseTunnelDurationCdf = lambda x: 3.8147e-6 / (x - 1) * (2.55328e8 - 4.20317e8 * x - math.sqrt(6.51925e16 - 2.06182e17 * x + 1.68178e17 * x**2) )
    tunnelDurationRV = inversionMethod(inverseTunnelDurationCdf)

    ggsn = Traditional_GGSN(env, tunnelDurationRV, options.numberOfSupportedParallelTunnels, options.transientPhaseDuration, sim_name)
    users = Users(env, tunnelInterArrivalTimeRV, ggsn, sim_name)

    simpy.simulate(env, until = options.duration)

    print("Writing results")
    ggsn.report(options.seed, options.duration)


if __name__ == '__main__':
    sim_name = "traditional_ggsn"
    main()