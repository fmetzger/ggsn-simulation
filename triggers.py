class DefaultStartupCondition:
    def __init__(self, ggsn, config):
        self._ggsn = ggsn
        self._instance_capacity = config.numberOfSupportedParallelTunnels

    def isMet(self, hourOfTheDay):
        return (self._ggsn.numberOfRunningInstances() * self._instance_capacity - self._ggsn.currentNumberOfTunnels()) < 2

class DefaultShutdownCondition:
    def __init__(self, ggsn, config):
        self._ggsn = ggsn
        self._instance_capacity = config.numberOfSupportedParallelTunnels

    def isMet(self, hourOfTheDay):
         total_capacity = self._ggsn.numberOfRunningInstances() * self._instance_capacity
         print("run_inst: %d, tuns: %d, max_t_per_inst: %d", self._ggsn.numberOfRunningInstances(), self._ggsn.currentNumberOfTunnels(), self._instance_capacity)

         return (total_capacity - self._ggsn.currentNumberOfTunnels()) >= self._instance_capacity * 2


