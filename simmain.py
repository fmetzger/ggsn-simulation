#!/usr/bin/pypy

import simpy

from simutil import *
from simclasses import *
from ggsn import *



def main():
    (options, args) = option_parse()
    config_dict = load_config('assets/sim.config')
    for k,v in config_dict.items():
        print ("{0} = {1}".format(k,v))

    env = simpy.Environment()
    setup_logger(options, config_dict, env)
    random.seed(options.seed)

    if options.ggsnType == "multiserver_ggsn" or options.ggsnType == "multiserver":
        ggsn = Multiserver_GGSN(env, options, config_dict)
    elif options.ggsnType == "traditional_ggsn" or options.ggsnType == "traditional":
        ggsn = Traditional_GGSN(env, options, config_dict)
    else:
        print("Error: No or invalid GGSN type")
        exit()

    
    users = Users(env, ggsn, options)
    env.simulate(until = config_dict["duration"])
    print("Writing results")
    ggsn.report(options.seed, config_dict["duration"])


if __name__ == '__main__':
    main()
