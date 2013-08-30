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

    instanceStartup = False
    instanceShutdown = False

    def __init__(self, env, options):
        Base_GGSN.__init__(self, env, options)
        
        self.instanceStartupTime = options.startupTime
        self._startupCondition = options.startupCondition(self, options)
        self.instanceShutdownTime = options.shutdownTime
        self._shutdownCondition = options.shutdownCondition(self, options)



        self.numberOfMaxInstances = 1000
        self.instances = simpy.Resource(self.env, capacity = self.numberOfMaxInstances)
        self.instances_monitor = monitoring.resource_monitor(self.instances, DurationBackend(self.numberOfMaxInstances, self.transientPhaseDuration))



    def numberOfRunningInstances(self):
        return self.instances.count

    def currentNumberOfTunnels(self):
        return self.tunnels.count

    def process(self):
        currentTime = self.env.now
        self.logger.info("New tunnel request at GGSN, currently %d/%d resources in use.", self.tunnels.count, self.tunnels.capacity)
        if currentTime >= self.transientPhaseDuration:
            self.numberOfTotalTunnels += 1

        if self.tunnels.count >= self.tunnels.capacity: ## capacity becomes 0 shortly after sim start, big issue as this will block any future tunnels
            self.numberOfTunnelsBlocked += 1
            self.logger.info("Tunnel request denied.")

        else:
            if not Multiserver_GGSN.instanceStartup and self._startupCondition.isMet(getHourOfTheDay(self.env.now)):
                Multiserver_GGSN.instanceStartup = True 
                yield self.env.timeout(self.instanceStartupTime)
                req = self.instances.request()
                #yield req
                self.logger.warn(self.numberOfRunningInstances())
                self.tunnels._capacity = self.numberOfSupportedParallelTunnels * self.numberOfRunningInstances()
                self.logger.warn("Spawning new GGSN instance, now at %d with total capacity %d", self.numberOfRunningInstances(), self.tunnels._capacity)
                Multiserver_GGSN.instanceStartup = False                
            elif Multiserver_GGSN.instanceStartup:
                self.logger.warn("Already spawning new GGSN, not spawning another instance.")
            else:
                self.logger.warn("startup_condition not fulfilled, not spawning another instance.")


            with self.tunnels.request() as request:
                yield request

                ## fetch the inverse cdf for the duration distribution for the current hour of day
                tunnelDuration = self.tunnelDurationRV(self.env.now)

                self.logger.info("Tunnel established, duration of %f", tunnelDuration)
                yield self.env.timeout(tunnelDuration)
            self.logger.info("Tunnel completed, now %d/%d resources in use.", self.tunnels.count, self.tunnels.capacity)

            if (self.numberOfRunningInstances() > 1) and (not Multiserver_GGSN.instanceShutdown) and (self._shutdownCondition.isMet(getHourOfTheDay(self.env.now))):
                self.logger.warn("run_inst: %d, tuns: %d, max_t_per_inst: %d, cond: %d", self.numberOfRunningInstances(), self.currentNumberOfTunnels(), self.numberOfSupportedParallelTunnels, self._shutdownCondition.isMet(getHourOfTheDay(self.env.now)))
                Multiserver_GGSN.instanceShutdown = True
                self.instances.release(self.instances.users[-1])
                self.tunnels._capacity = self.numberOfSupportedParallelTunnels * self.numberOfRunningInstances()
                self.logger.warn("Shutting down GGSN instance, now at %d", self.numberOfRunningInstances())
                yield self.env.timeout(self.instanceShutdownTime)
                Multiserver_GGSN.instanceShutdown = False

    def report(self, seed, simulationDuration):
        Base_GGSN.report(self, seed, simulationDuration)
        with open("%s/%s/instance_use_distribution_%d_%d.csv" % (self.resultsdir, self.name, self.numberOfSupportedParallelTunnels, simulationDuration), "a") as csvFile:
            resourceUseDistribution = self.resourceUseDistribution(self.instances_monitor)
            writer = csv.writer(csvFile, delimiter = ";")
            writer.writerow([seed] + resourceUseDistribution)





