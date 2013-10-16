import simpy
import monitoring

from simutil import *
from simclasses import *

class Base_GGSN():
    def __init__(self, env, options):
        self.env = env
        self.name = options.type
        self.seed = options.seed

        self.logger = logging.getLogger(options.type)
        inverseCdfs = loadHourlyDuration('assets/inverse_cdf.csv')
        self.tunnelDurationRV = lambda t: tunnelDuration(inverseCdfs, random.uniform(0,1), t)        

        self.numberOfSupportedParallelTunnels = options.numberOfSupportedParallelTunnels
        self.transientPhaseDuration = options.transientPhaseDuration

        self.numberOfTotalTunnels = 0
        self.numberOfTunnelsBlocked = 0

        self.tunnels = simpy.Resource(self.env, capacity = self.numberOfSupportedParallelTunnels)
        self.tunnels_monitor = monitoring.resource_monitor(self.tunnels, DurationBackend(self.numberOfSupportedParallelTunnels, self.transientPhaseDuration))

        self.resultsdir = "{0}/{1}/".format(options.results, self.name)
        self.resultsbasename = "_{0}_{1}.csv".format(self.numberOfSupportedParallelTunnels, options.duration)

    def resourceUseDistribution(self,monitor):
        return [duration/self.env.now for duration in monitor.data]

    def blockingProbability(self):
        if (self.numberOfTotalTunnels != 0):
            return float(self.numberOfTunnelsBlocked) / self.numberOfTotalTunnels
        else:
            return 0

    def meanResourceUtilization(self, distribution):
        return sum([i * distribution[i] for i in range(len(distribution))])

    def report(self):
        # mkdirs("%s/%s" % (self.resultsdir, self.name))
        mkdirs(self.resultsdir)
        with open("{0}resource_use_distribution{1}".format(self.resultsdir, self.resultsbasename), "a") as csvFile:
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([self.seed] + self.resourceUseDistribution(self.tunnels_monitor))
        with open("{0}metrics{1}".format(self.resultsdir, self.resultsbasename), "a") as csvFile:
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([self.seed, self.meanResourceUtilization(self.resourceUseDistribution(self.tunnels_monitor)), self.blockingProbability()])


class Traditional_GGSN(Base_GGSN):
    def __init__(self, env, options):
        Base_GGSN.__init__(self, env, options)

    def process(self):
        currentTime = self.env.now
        self.logger.info("New tunnel request at GGSN, currently %d/%d resources in use.", self.tunnels.count, self.numberOfSupportedParallelTunnels)
        if currentTime >= self.transientPhaseDuration:
            self.numberOfTotalTunnels += 1
        if self.tunnels.count != self.numberOfSupportedParallelTunnels:
            with self.tunnels.request() as request:
                yield request
                tunnelDuration = self.tunnelDurationRV(self.env.now)
                self.logger.info("Tunnel established, duration of %f", tunnelDuration)
                yield self.env.timeout(tunnelDuration)
            self.logger.info("Tunnel completed, now %d/%d resources in use.", self.tunnels.count, self.numberOfSupportedParallelTunnels)
        else:
            if currentTime >= self.transientPhaseDuration:
                self.numberOfTunnelsBlocked += 1
            self.logger.info("Tunnel request denied.")




class Multiserver_GGSN(Base_GGSN):

    def __init__(self, env, options):
        Base_GGSN.__init__(self, env, options)
        self.hv = Hypervisor(self, env, options)
        self.resultsbasename = "_{0}_{1}_{2}_{3}.csv".format(self.numberOfSupportedParallelTunnels, self.hv.numberOfMaxInstances, options.startupTime, options.duration)



    def currentNumberOfTunnels(self):
        return self.tunnels.count

    def process(self):
        currentTime = self.env.now
        self.logger.info("New tunnel request at GGSN, currently %d/%d resources in use.", self.tunnels.count, self.tunnels.capacity)
        if currentTime >= self.transientPhaseDuration:
            self.numberOfTotalTunnels += 1

        yield self.env.process(self.hv.check_and_increase_capacity())

        if self.tunnels.count >= self.tunnels.capacity:
            self.numberOfTunnelsBlocked += 1
            self.logger.info("Tunnel request denied.")

        else:
            with self.tunnels.request() as request:
                yield request
                
                tunnelDuration = self.tunnelDurationRV(self.env.now) ## fetch the inverse cdf for the duration distribution for the current hour of day
                self.logger.info("Tunnel established, duration of %f", tunnelDuration)
                yield self.env.timeout(tunnelDuration)
            self.logger.info("Tunnel completed, now %d/%d resources in use.", self.tunnels.count, self.tunnels.capacity)

            yield self.env.process(self.hv.check_and_reduce_capacity())

    def report(self):
        Base_GGSN.report(self)
        with open("{0}instance_use_distribution{1}".format(self.resultsdir, self.resultsbasename), "a") as csvFile:
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([self.seed] + self.resourceUseDistribution(self.hv.instances_monitor))





