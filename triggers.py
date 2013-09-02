class DefaultStartupCondition:
    def __init__(self, ggsn, hv, config):
        self._ggsn = ggsn
        self._hv = hv
        self._instance_capacity = config.numberOfSupportedParallelTunnels

    def isMet(self, hourOfTheDay):
        return (self._hv.number_of_running_instances() * self._instance_capacity - self._ggsn.currentNumberOfTunnels()) < 2

class DefaultShutdownCondition:
    def __init__(self, ggsn, hv, config):
        self._ggsn = ggsn
        self._hv = hv
        self._instance_capacity = config.numberOfSupportedParallelTunnels

    def isMet(self, hourOfTheDay):
         total_capacity = self._hv.number_of_running_instances() * self._instance_capacity
         return (total_capacity - self._ggsn.currentNumberOfTunnels()) >= self._instance_capacity * 2


