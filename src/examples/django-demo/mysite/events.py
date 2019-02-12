import eventlog
from django.http import HttpResponse


# The defaultEventHandler initializes a handler from settings defined
# either in django settings or environment (env overrides settings).
# If EVENTLOG_HOST is '', the defaultEventHandler will be a console handler.
eventHandler = eventlog.defaultEventHandler()
if eventHandler.isRemote():
    # if remote handler is enabled, clone the stream to console
    eventHandler.setReplica(eventlog.ConsoleEventHandler())


# counterAPI provides rest api for manipulating counter
class CounterAPI:

    def __init__(self, name, target=None, initialValue=0):
        self.counter = eventHandler.createTrackingValue(name, target, initialValue)

    def _makeResponse(self):
        return HttpResponse("value=%d\n" % self.counter.get(),
                            content_type='text/plain')

    def get(self, request):
        return self._makeResponse()

    def set(self, request, val):
        self.counter.set(int(val))
        return self._makeResponse()

    def inc(self, request, amt=1):
        self.counter.inc(int(amt))
        return self._makeResponse()
