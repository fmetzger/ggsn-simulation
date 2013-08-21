#!/usr/bin/pypy

import simpy

from simutil import *
from simclasses import *
from ggsn import *



def main():
    config_dict = load_config('assets/sim.config')
    options = option_parse(config_dict)
    #for k,v in config_dict.items():
    #    print ("{0} = {1}".format(k,v))

    env = simpy.Environment()
    setup_logger(options, env)
    random.seed(options.seed)

    if options.type =="multiserver":
        ggsn = Multiserver_GGSN(env, options)
    elif options.type  == "traditional":
        ggsn = Traditional_GGSN(env, options)
    else:
        print("Error: No or invalid GGSN type")
        exit()

    
    users = Users(env, ggsn, options)
    env.simulate(until = options.duration)
    print("Writing results")
    ggsn.report(options.seed, options.duration)


if __name__ == '__main__':
    main()
