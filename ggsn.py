import simpy
import monitoring

from simutil import *
from simclasses import *

class Base_GGSN():
    def __init__(self, env, options):
        self.env = env
        self.name = options.type

        self.resultsdir = options.results
        self.logger = logging.getLogger(options.type)
        inverseCdfs = loadHourlyDuration('assets/inverse_cdf.csv')
        self.tunnelDurationRV = lambda t: tunnelDuration(inverseCdfs, random.uniform(0,1), t)        

        self.numberOfSupportedParallelTunnels = options.numberOfSupportedParallelTunnels
        self.transientPhaseDuration = options.transientPhaseDuration

        self.numberOfTotalTunnels = 0
        self.numberOfTunnelsBlocked = 0

        self.tunnels = simpy.Resource(self.env, capacity = self.numberOfSupportedParallelTunnels)
        self.tunnels_monitor = monitoring.resource_monitor(self.tunnels, DurationBackend(self.numberOfSupportedParallelTunnels, self.transientPhaseDuration))

    def resourceUseDistribution(self,monitor):
        return [duration/self.env.now for duration in monitor.data]

    def blockingProbability(self):
        if (self.numberOfTotalTunnels != 0):
            return float(self.numberOfTunnelsBlocked) / self.numberOfTotalTunnels
        else:
            return 0

    def meanResourceUtilization(self, distribution):
        return sum([i * distribution[i] for i in range(len(distribution))])

    def report(self, seed, simulationDuration):
        mkdirs("%s/%s" % (self.resultsdir, self.name))
        with open("%s/%s/resource_use_distribution_%d_%d.csv" % (self.resultsdir, self.name, self.numberOfSupportedParallelTunnels, simulationDuration), "a") as csvFile:
            resourceUseDistribution = self.resourceUseDistribution(self.tunnels_monitor)
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([seed] + resourceUseDistribution)
        with open("%s/%s/metrics_%d_%d.csv" % (self.resultsdir, self.name, self.numberOfSupportedParallelTunnels, simulationDuration), "a") as csvFile:
            meanResourceUtilization = self.meanResourceUtilization(resourceUseDistribution)
            blockingProbability = self.blockingProbability()
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([seed, meanResourceUtilization, blockingProbability])


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


    def currentNumberOfTunnels(self):
        return self.tunnels.count

    def process(self):
        currentTime = self.env.now
        self.logger.info("New tunnel request at GGSN, currently %d/%d resources in use.", self.tunnels.count, self.tunnels.capacity)
        if currentTime >= self.transientPhaseDuration:
            self.numberOfTotalTunnels += 1

        yield self.env.start(self.hv.check_and_increase_capacity())

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

            yield self.env.start(self.hv.check_and_reduce_capacity())

    def report(self, seed, simulationDuration):
        Base_GGSN.report(self, seed, simulationDuration)
        with open("%s/%s/instance_use_distribution_%d_%d.csv" % (self.resultsdir, self.name, self.numberOfSupportedParallelTunnels, simulationDuration), "a") as csvFile:
            resourceUseDistribution = self.resourceUseDistribution(self.hv.instances_monitor)
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([seed] + resourceUseDistribution)





