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
        self.env.process(self.run())

    def run(self):
        while True:
            currentTime = self.env.now
            if (currentTime - self.lastNotification) > 1000:
                print("Time: %f" % self.env.now)
                self.lastNotification = currentTime
            nextArrival = self.tunnelInterArrivalTimeRV(currentTime)
            yield self.env.timeout(nextArrival)
            self.logger.info("New tunnel request by user")
            self.env.process(self.ggsn.process())



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

        self.numberOfMaxInstances = options.maxInstanceNumber
        self.instances = simpy.Resource(self.env, capacity = self.numberOfMaxInstances)
        self.instances_monitor = monitoring.resource_monitor(self.instances, DurationBackend(self.numberOfMaxInstances, self.ggsn.transientPhaseDuration))
        self.instances.request()   # we need to start with one server already available

    def number_of_running_instances(self):
        return self.instances.count

    def check_and_increase_capacity(self):
        if not Hypervisor.instanceStartup:
            if self.number_of_running_instances() < self.instances.capacity:
                if self._startupCondition.isMet(getHourOfTheDay(self.env.now)):
                    Hypervisor.instanceStartup = True 
                    yield self.env.timeout(self.instanceStartupTime)
                    
                    # TODO
                    ## sample code with a possible way to threat the blocking tunnel in the instance startup
                    #result = yield self.env.timeout(self.instanceStartupTime) | currentTunnelDuration
                    # if we only waited tunnel duration time and not the whole instance duration
                    #if self.env.timeout(self.instanceStartupTime) not in result:
                    #   do stuff
                    # return remaining tunnel time
                    # TODO

                    req = self.instances.request()
                    # yield req
                    self.ggsn.tunnels._capacity = self.ggsn.numberOfSupportedParallelTunnels * self.number_of_running_instances()
                    self.logger.info("Spawning new GGSN instance, now at %d with total capacity %d", self.number_of_running_instances(), self.ggsn.tunnels._capacity)
                    Hypervisor.instanceStartup = False
                else:
                    self.logger.info("startup_condition: %d, run_inst: %d, tuns: %d, max_t_per_inst: %d", self._startupCondition.isMet(getHourOfTheDay(self.env.now)), self.number_of_running_instances(), self.ggsn.currentNumberOfTunnels(), self.ggsn.numberOfSupportedParallelTunnels)
            else:
                self.logger.info("Instances at max capacity, not spawning another instance.")
        else:
            self.logger.info("Already spawning new GGSN, not spawning another instance.")

    def check_and_reduce_capacity(self):
        if (self.number_of_running_instances() > 1):
            if (not Hypervisor.instanceShutdown):
                if (self._shutdownCondition.isMet(getHourOfTheDay(self.env.now))):
                    self.logger.info("shutdown_cond: %d run_inst: %d, tuns: %d, max_t_per_inst: %d, ", self._shutdownCondition.isMet(getHourOfTheDay(self.env.now)), self.number_of_running_instances(), self.ggsn.currentNumberOfTunnels(), self.ggsn.numberOfSupportedParallelTunnels)
                    Hypervisor.instanceShutdown = True
                    yield self.env.timeout(self.instanceShutdownTime)
                    self.instances.release(self.instances.users[-1])
                    self.ggsn.tunnels._capacity = self.ggsn.numberOfSupportedParallelTunnels * self.number_of_running_instances()
                    Hypervisor.instanceShutdown = False
