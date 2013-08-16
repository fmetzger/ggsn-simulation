#!/usr/bin/pypy

import simpy

from simutil import *
from simclasses import *
from ggsn import Multiserver_GGSN



def main():
    (options, args) = option_parse()
    env = simpy.Environment()
    setup_logger(options, sim_name, env)

    print("Simulating for %d seconds (transient phase of %d seconds) with a support for %d parallel tunnels and seed %d." % (options.duration, options.transientPhaseDuration, options.numberOfSupportedParallelTunnels, options.seed))


    if options.shutdownCondition:
        shutdownCondition = eval(options.shutdownCondition)
    else:
        shutdownCondition = lambda tunnels, instances, instancecapacity: (instances*instancecapacity - tunnels) >= instancecapacity * 2


    random.seed(options.seed)
    interarrivalRates = loadHourlyRates('assets/interarrival_rates.csv')
    tunnelInterArrivalTimeRV = lambda t: random.expovariate(tunnelInterArrivalRate(interarrivalRates, t))

    inverseCdfs = loadHourlyDuration('assets/inverse_cdf.csv')
    tunnelDurationRV = lambda t: tunnelDuration(inverseCdfs, random.uniform(0,1), t)

    ggsn = Multiserver_GGSN(env, tunnelDurationRV, options.numberOfSupportedParallelTunnels, options.transientPhaseDuration, options.startupTime, options.shutdownTime, shutdownCondition, sim_name)
    users = Users(env, tunnelInterArrivalTimeRV, ggsn, sim_name)

    simpy.simulate(env, until = options.duration)

    print("Writing results")
    ggsn.report(options.seed, options.duration)


if __name__ == '__main__':
    sim_name = "multiserver_ggsn"
    main()
