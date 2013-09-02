import logging
import simpy
import monitoring

from simutil import *

class DurationBackend:
    def __init__(self, numberOfMaxResources, transientPhaseDuration):
        self.data = numpy.zeros(numberOfMaxResources + 1)
        self.currentTime = 0
        self.transientPhaseDuration = transientPhaseDuration

    def append(self, data):
        currentTime, numberOfResourcesInUse, queueLength = data
        if currentTime >= self.transientPhaseDuration:
            duration = currentTime - self.currentTime
            self.currentTime = currentTime
            try:
                self.data[numberOfResourcesInUse] += duration
            except IndexError:
                tmp = numpy.zeros(numberOfResourcesInUse + 1 - len(self.data))
                self.data = numpy.concatenate((self.data, tmp))
                self.data[numberOfResourcesInUse] += duration





class Users():
    def __init__(self, env, ggsn, options):
        self.env = env
        self.logger = logging.getLogger(options.type)
        interarrivalRates = loadHourlyRates('assets/interarrival_rates.csv')
        self.tunnelInterArrivalTimeRV = lambda t: random.expovariate(tunnelInterArrivalRate(interarrivalRates, t))
        self.ggsn = ggsn

        self.lastNotification = 0
        self.env.start(self.run())

    def run(self):
        while True:
            currentTime = self.env.now
            if (currentTime - self.lastNotification) > 1000:
                print("Time: %f" % self.env.now)
                self.lastNotification = currentTime
            nextArrival = self.tunnelInterArrivalTimeRV(currentTime)
            yield self.env.timeout(nextArrival)
            self.logger.info("New tunnel request by user")
            self.env.start(self.ggsn.process())



class Hypervisor():
    instanceStartup = False
    instanceShutdown = False

    def __init__(self, ggsn, env, options):
        self.env = env
        self.ggsn = ggsn
        self.logger = logging.getLogger(options.type)
        self.instanceStartupTime = options.startupTime
        self._startupCondition = options.startupCondition(self.ggsn, self, options)
        self.instanceShutdownTime = options.shutdownTime
        self._shutdownCondition = options.shutdownCondition(self.ggsn, self, options)

        self.numberOfMaxInstances = 1000
        self.instances = simpy.Resource(self.env, capacity = self.numberOfMaxInstances)
        self.instances_monitor = monitoring.resource_monitor(self.instances, DurationBackend(self.numberOfMaxInstances, self.ggsn.transientPhaseDuration))
        self.instances.request()   # we need to start with one server already available

    def number_of_running_instances(self):
        return self.instances.count

    def check_and_increase_capacity(self):
        print("check_and_increase_capacity")
        if not Hypervisor.instanceStartup:
            self.logger.warn("no instance startup in progress")
            if self._startupCondition.isMet(getHourOfTheDay(self.env.now)):
                Hypervisor.instanceStartup = True 
                # yield self.env.timeout(self.instanceStartupTime)
                with self.instances.request() as req:
                    yield req
                    self.logger.warn(self.number_of_running_instances())
                    self.ggsn.tunnels._capacity = self.ggsn.numberOfSupportedParallelTunnels * self.number_of_running_instances()
                    self.logger.warn("Spawning new GGSN instance, now at %d with total capacity %d", self.number_of_running_instances(), self.ggsn.tunnels._capacity)
                    Hypervisor.instanceStartup = False
            else:
                self.logger.warn("startup_condition not fulfilled, not spawning another instance.")         
        else:
            self.logger.warn("Already spawning new GGSN, not spawning another instance.")

    def check_and_reduce_capacity(self):
        self.logger.info("check_and_reduce_capacity")
        if (self.number_of_running_instances() > 1):
            self.logger.warn("level 1: %d", self.number_of_running_instances())
            if (not Hypervisor.instanceShutdown):
                self.logger.warn("level 2: %s", not Hypervisor.instanceShutdown)
                if (self._shutdownCondition.isMet(getHourOfTheDay(self.env.now))):
                    self.logger.warn("level 3: %s", self._shutdownCondition.isMet(getHourOfTheDay(self.env.now)))

                    self.logger.warn("run_inst: %d, tuns: %d, max_t_per_inst: %d, cond: %d", self.number_of_running_instances(), self.ggsn.currentNumberOfTunnels(), self.ggsn.numberOfSupportedParallelTunnels, self._shutdownCondition.isMet(getHourOfTheDay(self.env.now)))
                    Hypervisor.instanceShutdown = True
                    self.instances.release(self.instances.users[-1])
                    self.ggsn.tunnels._capacity = self.ggsn.numberOfSupportedParallelTunnels * self.number_of_running_instances()
                    self.logger.warn("Shutting down GGSN instance, now at %d", self.number_of_running_instances())
                    print(self.instanceShutdownTime)
                    # yield self.env.timeout(self.instanceShutdownTime)
                    Hypervisor.instanceShutdown = False
