"""
This module was rescued from a local copy before it was removed from simpy's
repo. It obviously is under simpy's original license, i.e. LGPL.
It will be removed 
"""

"""
This module contains SimPy's monitoring capabilities.

The :class:`Monitor` is the central class to collect and store data
from your simulation.

It can use different back ends to define how the data is stored (e.g.,
in plain lists, in a database or even in an Excel sheet if you want).
All back ends should inherit :class:`Backend`. SimPy has three built-in
back end types: :class:`ListBackend` (the default),
:class:`NamedtupleBackend` and :class:`PrinterBackend`.

You can also automatically collect data when a certain method is called
(e.g., ``Resource.request()`` or ``Container.put()``). The function
:func:`patch()` patches an object to automatically call
:meth:`Monitor.collect()` before or after a method call.

SimPy offers two shortcut functions to patch a resource
(:func:`resource_monitor()`) and a container/store
(:func:`container_monitor()`). They are using the collector functions
returned by :func:`resource_collector()` and
:func:`container_collector()`, respectively.

"""
import collections


class Monitor(object):
    """Monitors can be used to (semi-)automatically collect data from
    processes, resources and other objects involved in a simulation.

    A monitor consists of a collector and a back end. The collector is
    responsible for retrieving the required data from a process,
    resource or something else. The back end then stores that data in
    some place. By default, the :class:`ListBackend` is used which
    simply appends everything that the collector returns to a list.


    Before a monitor can be used, it has to be configured via
    :meth:`configure()`. You can then simply call :meth:`collect()` to
    to collect and add data to it. You can access the data via the
    :attr:`data` property.

    The monitor also offers a simple process :meth:`run()` that
    automatically collects data in user defined intervals.

    """
    def __init__(self):
        self._backend = None
        self._collector = None

    @property
    def data(self):
        """All collected data. Its type depends on the back end used."""
        return self._backend.data

    def run(self, env, collect_interval=1):
        """A simple process that calls :meth:`collect()` every
        *collect_interval* steps.

        *env* is a :class:`~simpy.Environment` instance.

        """
        while True:
            self.collect()
            yield env.timeout(collect_interval)

    def configure(self, collector, backend=None):
        """Configure the *collector* function and the *backend*.

        The collector can be any callable with no arguments. It should
        usually return a list or tuple with the collected values.

        Per default, the :class:`ListBackend` is used as back end. You
        can pass an instance of another back end type to change this.
        Back ends need to have *data* attribute and implement an
        *append()* method that takes that data returned by the collector
        and appends it to *data*.

        """
        self._collector = collector
        if not backend:
            backend = ListBackend()
        self._backend = backend

    def collect(self):
        """Call the collector and append the collected data to the monitor."""
        data = self._collector()
        self._backend.append(data)


class Backend(object):
    """Base class for all backends."""
    data = None

    def append(self, data):
        """Append *data* to ``self.data``."""
        raise NotImplementedError

def patch(obj, monitor, pre_call=(), post_call=()):
    """Monkey patch some of methods of *obj* to automatically call
    *monitor's* :meth:`~Monitor.collect()` method when they are called.

    *pre_call* and *post_call* are lists containing method names.

    Patch all methods in *pre_call* to call :meth:`Monitor.collect()`
    just before they are called. Patch all methods in *post_call* to
    call :meth:`Monitor.collect()` after they were called.  A method
    name can be in both lists at the same time.

    """
    def get_wrapper(obj, name, monitor, pre, post):
        orig_method = getattr(obj, name)

        def call_and_collect(*args, **kwargs):
            if pre:
                monitor.collect()
            ret = orig_method(*args, **kwargs)
            if post:
                monitor.collect()
            return ret

        return call_and_collect

    names = set(pre_call) | set(post_call)
    for name in names:
        wrapper = get_wrapper(obj, name, monitor, name in pre_call,
                              name in post_call)
        setattr(obj, name, wrapper)


def resource_monitor(resource, backend=None):
    """Shortcut for creating a resource monitor.

    The :class:`Monitor` returned is already configured. The *resource*
    is monkey patched to automatically call its
    :meth:`~Monitor.collect()` method before each *request* and
    *release*.

    It works for :class:`~simpy.resources.Resource` and its subclasses.
    It collects the current simulation time, the users and the
    the queue every time ``request()`` or ``release()`` were
    called (see :func:`resource_collector()` for details).

    You can optionally specify a custom *backend*.

    """
    monitor = Monitor()
    monitor.configure(resource_collector(resource), backend=backend)
    patch(resource, monitor, pre_call=('request', 'release'))
    return monitor


def resource_collector(resource, include_time=True):
    """Return a collector method for *resource*.

    This collector works for :class:`~simpy.resources.Resource` and its
    subclasses. It collects lists or process IDs for each, the
    resource's users and queue. If *include_time* is ``True``, it also
    collects the current simulation time.

    It either returns ``(time, user_ids, queued_ids)`` or ``(user_ids,
    queued_ids)``, where the time is a number (usually an ``int``, but
    maybe a ``float`` or something else) and the other values are
    lists of strings.

    This information allows you to analyze how many processes were using
    (or waiting for) the resource at any time and how long a process
    was using the resource or waiting for it.

    """
    def collector():
        data = (resource.count, len(resource.queue))
        #data = (
        #    [str(id(proc)) for proc in resource.get_users()],
        #    [str(id(proc)) for proc in resource.get_queued()],
        #)
        if include_time:
            data = (resource._env.now,) + data
        return data
    return collector
