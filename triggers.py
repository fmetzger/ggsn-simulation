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
         return (self._ggsn.numberOfRunningInstances() * self._instance_capacity - self._ggsn.currentNumberOfTunnels()) >= self._instance_capacity * 2


