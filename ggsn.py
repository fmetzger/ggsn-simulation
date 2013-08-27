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

        self.resources = simpy.Resource(self.env, capacity = self.numberOfSupportedParallelTunnels)
        self.resources_monitor = monitoring.resource_monitor(self.resources, DurationBackend(self.numberOfSupportedParallelTunnels, self.transientPhaseDuration))

    def resourceUseDistribution(self):
        return [duration/self.env.now for duration in self.resources_monitor.data]

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
            resourceUseDistribution = self.resourceUseDistribution()
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
        self.logger.info("New tunnel request at GGSN, currently %d/%d resources in use.", self.resources.count, self.numberOfSupportedParallelTunnels)
        if currentTime >= self.transientPhaseDuration:
            self.numberOfTotalTunnels += 1
        if self.resources.count != self.numberOfSupportedParallelTunnels:
            with self.resources.request() as request:
                yield request
                tunnelDuration = self.tunnelDurationRV(self.env.now)
                self.logger.info("Tunnel established, duration of %f", tunnelDuration)
                yield self.env.timeout(tunnelDuration)
            self.logger.info("Tunnel completed, now %d/%d resources in use.", self.resources.count, self.numberOfSupportedParallelTunnels)
        else:
            if currentTime >= self.transientPhaseDuration:
                self.numberOfTunnelsBlocked += 1
            self.logger.info("Tunnel request denied.")


class Multiserver_GGSN(Base_GGSN):
    def __init__(self, env, options):
        Base_GGSN.__init__(self, env, options)
        
        self.instanceStartupTime = options.startupTime
        self._startupCondition = options.startupCondition(self, options)
        self.instanceShutdownTime = options.shutdownTime
        self._shutdownCondition = options.shutdownCondition(self, options)

        self._numberOfRunningInstances = 1
        self.instanceStartup = False
        self.instanceShutdown = False


    def numberOfRunningInstances(self):
        return self._numberOfRunningInstances

    def currentNumberOfTunnels(self):
        return self.resources.count

    def process(self):
        currentTime = self.env.now
        self.logger.info("New tunnel request at GGSN, currently %d/%d resources in use.", self.resources.count, self.resources.capacity)
        if currentTime >= self.transientPhaseDuration:
            self.numberOfTotalTunnels += 1

        if self.resources.count >= self.resources.capacity:
            self.numberOfTunnelsBlocked += 1
            self.logger.info("Tunnel request denied.")

        else:
            if not self.instanceStartup and self._startupCondition.isMet(getHourOfTheDay(self.env.now)):
                self.instanceStartup = True 
                yield self.env.timeout(self.instanceStartupTime)
                self._numberOfRunningInstances += 1
                self.resources._capacity = self.numberOfSupportedParallelTunnels * self._numberOfRunningInstances
                self.logger.warn("Spawning new GGSN instance, now at %d", self._numberOfRunningInstances)
                self.instanceStartup = False                
            elif self.instanceStartup:
                self.logger.info("Already spawning new GGSN, not spawning another instance.")
            else:
                self.logger.info("startup_condition not fulfilled, not spawning another instance.")


            with self.resources.request() as request:
                yield request

                ## fetch the inverse cdf for the duration distribution for the current hour of day
                # tunnelDuration = self.tunnelDurationRV()
                tunnelDuration = self.tunnelDurationRV(self.env.now)

                self.logger.info("Tunnel established, duration of %f", tunnelDuration)
                yield self.env.timeout(tunnelDuration)
            self.logger.info("Tunnel completed, now %d/%d resources in use.", self.resources.count, self.resources.capacity)

            if not self.instanceShutdown and self._shutdownCondition.isMet(getHourOfTheDay(self.env.now)):
                self.instanceShutdown = True
                self._numberOfRunningInstances -= 1
                self.resources._capacity = self.numberOfSupportedParallelTunnels * self._numberOfRunningInstances
                self.logger.warn("Shutting down GGSN instance, now at %d", self._numberOfRunningInstances)
                yield self.env.timeout(self.instanceShutdownTime)
                self.instanceShutdown = False












